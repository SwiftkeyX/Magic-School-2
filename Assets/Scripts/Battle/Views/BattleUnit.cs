using System.Collections;
using UnityEngine;

namespace MagicSchool.Battle
{
    public class BattleUnit : MonoBehaviour
    {
        [Header("Health Bar")]
        [SerializeField, Range(0.2f, 2f)]  private float _barWidth   = 0.8f;
        [SerializeField, Range(0.02f, 0.5f)] private float _barHeight  = 0.14f;
        [SerializeField, Range(0f, 2f)]    private float _barYOffset = 0.65f;

        [Header("Animation")]
        [SerializeField, Range(0.02f, 1f)] private float _moveAnimDuration    = 0.15f;
        [SerializeField, Range(0.05f, 1f)] private float _attackLungePercent  = 0.3f;
        [SerializeField, Range(0.01f, 0.5f)] private float _attackLungeDuration = 0.05f;
        [SerializeField, Range(0.01f, 0.5f)] private float _attackSnapDuration  = 0.08f;
        [SerializeField, Range(0.05f, 2f)] private float _deathFadeDuration   = 0.4f;

        [Header("Skill Visuals (stubs — see Skill.md)")]
        [SerializeField] private Color _manaBarColor = new Color(0.25f, 0.55f, 1f, 1f);
        [SerializeField, Range(0.2f, 3f)] private float _castTextDuration     = 1.0f;
        [SerializeField, Range(0.1f, 2f)] private float _castTextRiseDistance = 0.5f;

        public string CombatantId { get; private set; }
        public HexCoord CurrentCell { get; private set; }

        private Coroutine _activeCoroutine;
        private SpriteRenderer _sprite;

        // Health bar child renderer
        private SpriteRenderer _hpFill;

        // Mana bar child renderer (see the skill-visual stubs at the bottom of this file)
        private SpriteRenderer _manaFill;

        // Casting flash state
        private Color _preCastColor;
        private bool  _isCastingVisualActive;

        private void Awake()
        {
            _sprite = GetComponent<SpriteRenderer>();
        }

        // removed: OnMouseDown() -> HeroSelection.Select(), and the BoxCollider2D that Awake()
        // auto-added purely to receive that click. HeroSelection had zero subscribers, so the
        // click did nothing; the collider existed only to service it.

        public void Init(string combatantId, HexCoord startCell)
        {
            CombatantId = combatantId;
            CurrentCell = startCell;
        }

        // Appearance comes from the hero's authored HeroDataSO asset (via CombatantSnapshot).
        // A null icon falls back to the procedural square, so a half-authored hero is still
        // visible and correctly tinted rather than invisible.
        public void SetVisual(Sprite icon, Color tint)
        {
            if (_sprite == null) _sprite = GetComponent<SpriteRenderer>();
            if (_sprite == null) return;

            _sprite.sprite = icon != null ? icon : HexSpriteGenerator.GetFallbackSprite();
            _sprite.color  = tint;
        }

        public void InitHealthBar(int currentHP, int maxHP)
        {
            Sprite slicedCenter = MakeSlicedSprite(new Vector2(0.5f, 0.5f));
            Sprite slicedLeft   = MakeSlicedSprite(new Vector2(0f,   0.5f));

            // Background — centered, dark gray
            var bg = new GameObject("HPBar_BG");
            bg.transform.SetParent(transform, false);
            bg.transform.localPosition = new Vector3(0f, _barYOffset, 0f);
            var bgSr = bg.AddComponent<SpriteRenderer>();
            bgSr.sprite       = slicedCenter;
            bgSr.drawMode     = SpriteDrawMode.Sliced;
            bgSr.size         = new Vector2(_barWidth, _barHeight);
            bgSr.color        = new Color(0.1f, 0.1f, 0.1f, 1f);
            bgSr.sortingOrder = 2;

            // Fill — left-pivoted so size shrinks rightward
            var fill = new GameObject("HPBar_Fill");
            fill.transform.SetParent(transform, false);
            fill.transform.localPosition = new Vector3(-_barWidth * 0.5f, _barYOffset, -0.01f);
            var fillSr = fill.AddComponent<SpriteRenderer>();
            fillSr.sprite       = slicedLeft;
            fillSr.drawMode     = SpriteDrawMode.Sliced;
            fillSr.size         = new Vector2(_barWidth, _barHeight);
            fillSr.color        = Color.green;
            fillSr.sortingOrder = 3;
            _hpFill = fillSr;

            UpdateHP(currentHP, maxHP);
        }

        public void UpdateHP(int current, int max)
        {
            if (_hpFill == null || max <= 0) return;
            float ratio = Mathf.Clamp01((float)current / max);
            _hpFill.size  = new Vector2(Mathf.Max(0.001f, _barWidth * ratio), _barHeight);
            _hpFill.color = ratio > 0.5f
                ? Color.Lerp(Color.yellow, Color.green,  (ratio - 0.5f) * 2f)
                : Color.Lerp(Color.red,    Color.yellow, ratio * 2f);
        }

        // Creates a 9-sliced white square sprite with the given pivot.
        private static Sprite MakeSlicedSprite(Vector2 pivot)
        {
            const int size = 8;
            var tex = new Texture2D(size, size, TextureFormat.RGBA32, false);
            var px  = new Color32[size * size];
            for (int i = 0; i < px.Length; i++) px[i] = new Color32(255, 255, 255, 255);
            tex.SetPixels32(px);
            tex.Apply();
            tex.filterMode = FilterMode.Point;
            // 2-pixel border on all sides → valid 9-slice
            return Sprite.Create(tex, new Rect(0, 0, size, size), pivot,
                                 (float)size, 0, SpriteMeshType.FullRect,
                                 new Vector4(2, 2, 2, 2));
        }

        // Lerp-slide to a new cell world position.
        public void MoveTo(Vector3 worldPos, HexCoord newCell)
        {
            CurrentCell = newCell;
            if (_activeCoroutine != null) StopCoroutine(_activeCoroutine);
            _activeCoroutine = StartCoroutine(LerpMove(worldPos));
        }

        private IEnumerator LerpMove(Vector3 target)
        {
            Vector3 start = transform.position;
            float elapsed = 0f;
            while (elapsed < _moveAnimDuration)
            {
                elapsed += Time.deltaTime;
                transform.position = Vector3.Lerp(start, target, elapsed / _moveAnimDuration);
                yield return null;
            }
            transform.position = target;
            _activeCoroutine = null;
        }

        // Brief lunge toward target position, then snap back.
        public void PlayAttackAnim(Vector3 targetWorldPos)
        {
            if (_activeCoroutine != null) StopCoroutine(_activeCoroutine);
            _activeCoroutine = StartCoroutine(AttackLunge(targetWorldPos));
        }

        private IEnumerator AttackLunge(Vector3 target)
        {
            Vector3 origin   = transform.position;
            Vector3 lungePos = Vector3.Lerp(origin, target, _attackLungePercent);

            float elapsed = 0f;
            while (elapsed < _attackLungeDuration)
            {
                elapsed += Time.deltaTime;
                transform.position = Vector3.Lerp(origin, lungePos, elapsed / _attackLungeDuration);
                yield return null;
            }

            elapsed = 0f;
            while (elapsed < _attackSnapDuration)
            {
                elapsed += Time.deltaTime;
                transform.position = Vector3.Lerp(lungePos, origin, elapsed / _attackSnapDuration);
                yield return null;
            }

            transform.position = origin;
            _activeCoroutine = null;
        }

        // Fade out and self-destruct.
        public void PlayDeathAnim()
        {
            if (_activeCoroutine != null) StopCoroutine(_activeCoroutine);
            _activeCoroutine = StartCoroutine(FadeAndDestroy());
        }

        private IEnumerator FadeAndDestroy()
        {
            if (_sprite == null) { Destroy(gameObject); yield break; }

            Color c = _sprite.color;
            float elapsed = 0f;
            while (elapsed < _deathFadeDuration)
            {
                elapsed += Time.deltaTime;
                float a = 1f - (elapsed / _deathFadeDuration);
                c.a = a;
                _sprite.color = c;
                if (_hpFill != null)
                {
                    Color fc = _hpFill.color; fc.a = a; _hpFill.color = fc;
                }
                yield return null;
            }

            Destroy(gameObject);
        }

        // ── Skill visuals (stubs — see Skill.md "Visual / Audio Requirements") ──────────────
        // NOT CURRENTLY CALLED. The resolver's OnSkillCast/OnManaChanged events were removed in
        // the teardown, so the Skill system's only output today is Debug.Log — meaning a designer
        // tuning MaxMana/SkillMultiplier gets no in-game feedback at all. Skill.md keeps these
        // hooks deliberately, for the pass that re-adds the events that drive them. They are
        // retained on that basis, not because anything reaches them today.

        public void InitManaBar(int current, int max)
        {
            Sprite slicedCenter = MakeSlicedSprite(new Vector2(0.5f, 0.5f));
            Sprite slicedLeft   = MakeSlicedSprite(new Vector2(0f,   0.5f));
            float  manaYOffset  = _barYOffset - _barHeight - 0.03f;   // stacked just below the HP bar

            var bg = new GameObject("ManaBar_BG");
            bg.transform.SetParent(transform, false);
            bg.transform.localPosition = new Vector3(0f, manaYOffset, 0f);
            var bgSr = bg.AddComponent<SpriteRenderer>();
            bgSr.sprite       = slicedCenter;
            bgSr.drawMode     = SpriteDrawMode.Sliced;
            bgSr.size         = new Vector2(_barWidth, _barHeight);
            bgSr.color        = new Color(0.1f, 0.1f, 0.1f, 1f);
            bgSr.sortingOrder = 2;

            var fill = new GameObject("ManaBar_Fill");
            fill.transform.SetParent(transform, false);
            fill.transform.localPosition = new Vector3(-_barWidth * 0.5f, manaYOffset, -0.01f);
            var fillSr = fill.AddComponent<SpriteRenderer>();
            fillSr.sprite       = slicedLeft;
            fillSr.drawMode     = SpriteDrawMode.Sliced;
            fillSr.size         = new Vector2(_barWidth, _barHeight);
            fillSr.color        = _manaBarColor;
            fillSr.sortingOrder = 3;
            _manaFill = fillSr;

            UpdateMana(current, max);
        }

        public void UpdateMana(int current, int max)
        {
            if (_manaFill == null || max <= 0) return;
            float ratio = Mathf.Clamp01((float)current / max);
            _manaFill.size = new Vector2(Mathf.Max(0.001f, _barWidth * ratio), _barHeight);
        }

        // Flat color swap rather than a coroutine — a cast lockout is only 1–2 ticks, too brief
        // for a readable animation.
        public void SetCastingVisual(bool active)
        {
            if (_sprite == null) return;
            if (active)
            {
                if (_isCastingVisualActive) return;
                _isCastingVisualActive = true;
                _preCastColor = _sprite.color;
                _sprite.color = Color.white;
            }
            else
            {
                if (!_isCastingVisualActive) return;
                _isCastingVisualActive = false;
                _sprite.color = _preCastColor;
            }
        }

        // Runs on its own coroutine (not _activeCoroutine) so a cast announcement never cancels,
        // or gets cancelled by, a movement/attack/death animation.
        public void PlayCastText(string skillName)
        {
            StartCoroutine(ShowCastText(skillName));
        }

        private IEnumerator ShowCastText(string skillName)
        {
            var go = new GameObject("CastText");
            go.transform.SetParent(transform, false);
            go.transform.localPosition = new Vector3(0f, _barYOffset + 0.3f, -0.02f);

            var tm = go.AddComponent<TextMesh>();
            tm.text          = skillName;
            tm.characterSize = 0.1f;
            tm.fontSize      = 32;
            tm.anchor        = TextAnchor.MiddleCenter;
            tm.alignment     = TextAlignment.Center;
            tm.color         = Color.cyan;

            Vector3 start = go.transform.localPosition;
            Vector3 end   = start + new Vector3(0f, _castTextRiseDistance, 0f);
            float elapsed = 0f;
            while (elapsed < _castTextDuration)
            {
                elapsed += Time.deltaTime;
                float t = elapsed / _castTextDuration;
                go.transform.localPosition = Vector3.Lerp(start, end, t);
                var c = tm.color;
                c.a = 1f - t;
                tm.color = c;
                yield return null;
            }

            Destroy(go);
        }
    }
}
