using System.Collections;
using UnityEngine;

namespace MagicSchool.Battle
{
    public class BattleUnit : MonoBehaviour
    {
        public string CombatantId { get; private set; }
        public string HeroSelectionId { get; private set; }
        public HexCoord CurrentCell { get; private set; }

        private Coroutine _activeCoroutine;
        private SpriteRenderer _sprite;

        // Health bar child renderers
        private SpriteRenderer _hpFill;
        private int _maxHP;

        // Mana bar child renderer
        private SpriteRenderer _manaFill;

        // Casting flash state
        private Color _preCastColor;
        private bool  _isCastingVisualActive;

        private const float MoveAnimDuration   = 0.15f;
        private const float AttackLungePercent = 0.3f;
        private const float AttackLungeDuration = 0.05f;
        private const float AttackSnapDuration  = 0.08f;
        private const float DeathFadeDuration   = 0.4f;
        private const float CastTextDuration    = 1.0f;
        private const float CastTextRiseDistance = 0.5f;

        private const float BarWidth   = 0.8f;
        private const float BarHeight  = 0.14f;
        private const float BarYOffset = 0.65f;
        private const float ManaBarYOffset = BarYOffset - BarHeight - 0.03f;  // stacked just below the HP bar
        private static readonly Color ManaBarColor = new Color(0.25f, 0.55f, 1f, 1f);

        private void Awake()
        {
            _sprite = GetComponent<SpriteRenderer>();

            if (GetComponent<Collider2D>() == null)
            {
                var col = gameObject.AddComponent<BoxCollider2D>();
                col.size = new Vector2(0.9f, 0.9f);
            }
        }

        private void OnMouseDown() => HeroSelection.Select(HeroSelectionId);

        public void Init(string combatantId, HexCoord startCell, string heroSelectionId = null)
        {
            CombatantId = combatantId;
            HeroSelectionId = heroSelectionId ?? combatantId;
            CurrentCell = startCell;
        }

        public void InitHealthBar(int currentHP, int maxHP)
        {
            _maxHP = maxHP;
            Sprite slicedCenter = MakeSlicedSprite(new Vector2(0.5f, 0.5f));
            Sprite slicedLeft   = MakeSlicedSprite(new Vector2(0f,   0.5f));

            // Background — centered, dark gray
            var bg = new GameObject("HPBar_BG");
            bg.transform.SetParent(transform, false);
            bg.transform.localPosition = new Vector3(0f, BarYOffset, 0f);
            var bgSr = bg.AddComponent<SpriteRenderer>();
            bgSr.sprite       = slicedCenter;
            bgSr.drawMode     = SpriteDrawMode.Sliced;
            bgSr.size         = new Vector2(BarWidth, BarHeight);
            bgSr.color        = new Color(0.1f, 0.1f, 0.1f, 1f);
            bgSr.sortingOrder = 2;

            // Fill — left-pivoted so size shrinks rightward
            var fill = new GameObject("HPBar_Fill");
            fill.transform.SetParent(transform, false);
            fill.transform.localPosition = new Vector3(-BarWidth * 0.5f, BarYOffset, -0.01f);
            var fillSr = fill.AddComponent<SpriteRenderer>();
            fillSr.sprite       = slicedLeft;
            fillSr.drawMode     = SpriteDrawMode.Sliced;
            fillSr.size         = new Vector2(BarWidth, BarHeight);
            fillSr.color        = Color.green;
            fillSr.sortingOrder = 3;
            _hpFill = fillSr;

            UpdateHP(currentHP, maxHP);
        }

        public void UpdateHP(int current, int max)
        {
            if (_hpFill == null) return;
            float ratio = Mathf.Clamp01((float)current / max);
            _hpFill.size  = new Vector2(Mathf.Max(0.001f, BarWidth * ratio), BarHeight);
            _hpFill.color = ratio > 0.5f
                ? Color.Lerp(Color.yellow, Color.green,  (ratio - 0.5f) * 2f)
                : Color.Lerp(Color.red,    Color.yellow, ratio * 2f);
        }

        // Mirrors InitHealthBar exactly, just stacked below it with a flat color —
        // mana doesn't need a health-style danger gradient.
        public void InitManaBar(int current, int max)
        {
            Sprite slicedCenter = MakeSlicedSprite(new Vector2(0.5f, 0.5f));
            Sprite slicedLeft   = MakeSlicedSprite(new Vector2(0f,   0.5f));

            var bg = new GameObject("ManaBar_BG");
            bg.transform.SetParent(transform, false);
            bg.transform.localPosition = new Vector3(0f, ManaBarYOffset, 0f);
            var bgSr = bg.AddComponent<SpriteRenderer>();
            bgSr.sprite       = slicedCenter;
            bgSr.drawMode     = SpriteDrawMode.Sliced;
            bgSr.size         = new Vector2(BarWidth, BarHeight);
            bgSr.color        = new Color(0.1f, 0.1f, 0.1f, 1f);
            bgSr.sortingOrder = 2;

            var fill = new GameObject("ManaBar_Fill");
            fill.transform.SetParent(transform, false);
            fill.transform.localPosition = new Vector3(-BarWidth * 0.5f, ManaBarYOffset, -0.01f);
            var fillSr = fill.AddComponent<SpriteRenderer>();
            fillSr.sprite       = slicedLeft;
            fillSr.drawMode     = SpriteDrawMode.Sliced;
            fillSr.size         = new Vector2(BarWidth, BarHeight);
            fillSr.color        = ManaBarColor;
            fillSr.sortingOrder = 3;
            _manaFill = fillSr;

            UpdateMana(current, max);
        }

        public void UpdateMana(int current, int max)
        {
            if (_manaFill == null || max <= 0) return;
            float ratio = Mathf.Clamp01((float)current / max);
            _manaFill.size = new Vector2(Mathf.Max(0.001f, BarWidth * ratio), BarHeight);
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
            while (elapsed < MoveAnimDuration)
            {
                elapsed += Time.deltaTime;
                transform.position = Vector3.Lerp(start, target, elapsed / MoveAnimDuration);
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
            Vector3 origin = transform.position;
            Vector3 lungePos = Vector3.Lerp(origin, target, AttackLungePercent);

            float elapsed = 0f;
            while (elapsed < AttackLungeDuration)
            {
                elapsed += Time.deltaTime;
                transform.position = Vector3.Lerp(origin, lungePos, elapsed / AttackLungeDuration);
                yield return null;
            }

            elapsed = 0f;
            while (elapsed < AttackSnapDuration)
            {
                elapsed += Time.deltaTime;
                transform.position = Vector3.Lerp(lungePos, origin, elapsed / AttackSnapDuration);
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
            while (elapsed < DeathFadeDuration)
            {
                elapsed += Time.deltaTime;
                float a = 1f - (elapsed / DeathFadeDuration);
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

        // Flashes the sprite white for the duration of Casting/Channeling (cast
        // lockout is only 1-2 ticks, too brief for a readable rotation, so a flat
        // color swap is used instead). No coroutine — driven directly by the
        // resolver's CastState transitions via BattleBoardManager.
        public void SetCastingVisual(bool active)
        {
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

        // Stateless one-shot floating text — runs on its own coroutine (not
        // _activeCoroutine) so a skill-cast announcement never cancels or gets
        // cancelled by movement/attack/death animations. Adds no new fields.
        public void PlayCastText(string skillName)
        {
            StartCoroutine(ShowCastText(skillName));
        }

        private IEnumerator ShowCastText(string skillName)
        {
            var go = new GameObject("CastText");
            go.transform.SetParent(transform, false);
            go.transform.localPosition = new Vector3(0f, BarYOffset + 0.3f, -0.02f);

            var tm = go.AddComponent<TextMesh>();
            tm.text            = skillName;
            tm.characterSize   = 0.1f;
            tm.fontSize        = 32;
            tm.anchor          = TextAnchor.MiddleCenter;
            tm.alignment       = TextAlignment.Center;
            tm.color           = Color.cyan;

            Vector3 start = go.transform.localPosition;
            Vector3 end   = start + new Vector3(0f, CastTextRiseDistance, 0f);
            float elapsed = 0f;
            while (elapsed < CastTextDuration)
            {
                elapsed += Time.deltaTime;
                float t = elapsed / CastTextDuration;
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
