using UnityEngine;
using UnityEngine.UIElements;

namespace MagicSchool.Battle
{
    /// <summary>
    /// Renders the Battle scene HUD via UI Toolkit.
    ///
    /// Owns: outcome overlay, speed-up indicator. All in-battle visual feedback
    /// (unit attacks, HP, defeats) is owned by BattleBoardManager on the hex board —
    /// BattleHUD does not duplicate it.
    ///
    /// Pure visual listener — never writes game state. The "Continue" button just
    /// hides the overlay (removed: RunManager.Instance.CompleteBattlePhase() handshake
    /// — meta-progression system, rebuilding fresh).
    ///
    /// AutoBattleResolver has no static Instance, so the reference is Inspector-wired
    /// via [SerializeField] _resolver. No FindObjectOfType anywhere in this file.
    /// </summary>
    public class BattleHUD : MonoBehaviour
    {
        // ── Inspector reference ───────────────────────────────────────────────
        [SerializeField] private AutoBattleResolver _resolver;

        // ── UIDocument ────────────────────────────────────────────────────────
        private UIDocument    _document;
        private VisualElement _root;

        // ── Structural elements ───────────────────────────────────────────────
        private Label _speedIndicator;

        // ── Outcome overlay ───────────────────────────────────────────────────
        private VisualElement _outcomeOverlay;
        private Label         _outcomeTitle;
        private Label         _outcomeSub;
        private Button        _continueButton;

        // ── Lifecycle ─────────────────────────────────────────────────────────

        private void Awake()
        {
            _document = GetComponent<UIDocument>();
            if (_document == null)
            {
                Debug.LogError("[BattleHUD] UIDocument component not found on this GameObject.");
                enabled = false;
                return;
            }

            _document.sortingOrder = BattleUISortOrder.BattleHUD;
            _root = _document.rootVisualElement;

            // Cache element references — never call Q<> outside Awake
            _speedIndicator = _root.Q<Label>("speed-indicator");
            _outcomeOverlay = _root.Q<VisualElement>("outcome-overlay");
            _outcomeTitle   = _root.Q<Label>("outcome-title");
            _outcomeSub     = _root.Q<Label>("outcome-sub");
            _continueButton = _root.Q<Button>("continue-button");

            // Wire Continue button in code — never rely on Inspector wiring
            if (_continueButton != null)
            {
                _continueButton.SetEnabled(false);
                _continueButton.clicked += OnContinueClicked;
            }

            // Initial display state
            SetDisplay(_outcomeOverlay, false);
            SetDisplay(_speedIndicator, false);
        }

        private void OnEnable()
        {
            if (_resolver == null)
            {
                Debug.LogWarning("[BattleHUD] _resolver not assigned; events not subscribed. " +
                                 "Assign AutoBattleResolver via Inspector.");
                return;
            }

            _resolver.OnBattleComplete += HandleBattleComplete;

            if (InputHandler.Instance != null)
            {
                InputHandler.Instance.OnSpeedUpStarted   += HandleSpeedUpStarted;
                InputHandler.Instance.OnSpeedUpCancelled += HandleSpeedUpCancelled;
            }
        }

        private void OnDisable()
        {
            if (_resolver != null)
            {
                _resolver.OnBattleComplete -= HandleBattleComplete;
            }

            if (InputHandler.Instance != null)
            {
                InputHandler.Instance.OnSpeedUpStarted   -= HandleSpeedUpStarted;
                InputHandler.Instance.OnSpeedUpCancelled -= HandleSpeedUpCancelled;
            }
        }

        // ── Event handlers ────────────────────────────────────────────────────

        private void HandleBattleComplete(BattleResult result)
        {
            if (_outcomeOverlay == null) return;

            SetDisplay(_outcomeOverlay, true);

            if (_outcomeTitle != null)
                _outcomeTitle.text = result.Won ? "Victory!" : "Defeated";

            if (_outcomeSub != null)
            {
                bool showSub = result.TimedOut;
                _outcomeSub.text = "(Time Limit)";
                SetDisplay(_outcomeSub, showSub);
            }

            // Enable Continue only after battle is complete (GDD AC)
            if (_continueButton != null)
                _continueButton.SetEnabled(true);

            Debug.Log($"[BattleHUD] Outcome overlay shown — " +
                      $"{(result.Won ? "Victory" : "Defeated")}" +
                      $"{(result.TimedOut ? " (Time Limit)" : string.Empty)}");
        }

        // ── Speed-up indicator ────────────────────────────────────────────────

        private void HandleSpeedUpStarted()
        {
            SetDisplay(_speedIndicator, true);
        }

        private void HandleSpeedUpCancelled()
        {
            SetDisplay(_speedIndicator, false);
        }

        // ── Continue button ───────────────────────────────────────────────────

        private void OnContinueClicked()
        {
            // removed: RunManager.Instance.CompleteBattlePhase() handshake — meta-progression
            // system, rebuilding fresh. Continue just re-hides the overlay for now.
            if (_continueButton != null)
                _continueButton.SetEnabled(false);

            SetDisplay(_outcomeOverlay, false);
        }

        // ── Helpers ───────────────────────────────────────────────────────────

        private static void SetDisplay(VisualElement el, bool visible)
        {
            if (el != null)
                el.style.display = visible ? DisplayStyle.Flex : DisplayStyle.None;
        }
    }
}
