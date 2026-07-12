using System;
using UnityEngine;
using UnityEngine.InputSystem;

namespace MagicSchool.Battle
{
    public class InputHandler : MonoBehaviour
    {
        public static InputHandler Instance { get; private set; }

        public bool IsInputEnabled { get; private set; } = true;

        public event Action OnCancelPressed;
        public event Action OnConfirmPressed;
        public event Action OnSpeedUpStarted;
        public event Action OnSpeedUpCancelled;

        private MagicTutorInputActions _inputActions;

        private void Awake()
        {
            if (Instance != null)
            {
                Debug.LogWarning($"[InputHandler] Duplicate instance found on {gameObject.name}. Destroying duplicate.");
                Destroy(gameObject);
                return;
            }

            Instance = this;

            _inputActions = new MagicTutorInputActions();

            // Wire up callbacks
            _inputActions.Gameplay.Cancel.performed += OnCancelPerformed;
            _inputActions.Gameplay.Confirm.performed += OnConfirmPerformed;
            _inputActions.Gameplay.SpeedUp.started += OnSpeedUpStartedCallback;
            _inputActions.Gameplay.SpeedUp.canceled += OnSpeedUpCanceledCallback;
        }

        private void OnEnable()
        {
            if (_inputActions != null)
            {
                _inputActions.Enable();
            }
        }

        private void OnDisable()
        {
            if (_inputActions != null)
            {
                _inputActions.Disable();
            }
        }

        private void OnDestroy()
        {
            if (_inputActions != null)
            {
                _inputActions.Gameplay.Cancel.performed -= OnCancelPerformed;
                _inputActions.Gameplay.Confirm.performed -= OnConfirmPerformed;
                _inputActions.Gameplay.SpeedUp.started -= OnSpeedUpStartedCallback;
                _inputActions.Gameplay.SpeedUp.canceled -= OnSpeedUpCanceledCallback;
                _inputActions.Dispose();
            }
        }

        public void EnableGameplayInput()
        {
            IsInputEnabled = true;
            Debug.Log("[InputHandler] Gameplay input enabled.");
        }

        public void DisableGameplayInput()
        {
            IsInputEnabled = false;
            Debug.Log("[InputHandler] Gameplay input disabled.");
        }

        private void OnCancelPerformed(InputAction.CallbackContext ctx)
        {
            if (IsInputEnabled)
            {
                OnCancelPressed?.Invoke();
            }
        }

        private void OnConfirmPerformed(InputAction.CallbackContext ctx)
        {
            if (IsInputEnabled)
            {
                OnConfirmPressed?.Invoke();
            }
        }

        private void OnSpeedUpStartedCallback(InputAction.CallbackContext ctx)
        {
            if (IsInputEnabled)
            {
                OnSpeedUpStarted?.Invoke();
            }
        }

        private void OnSpeedUpCanceledCallback(InputAction.CallbackContext ctx)
        {
            if (IsInputEnabled)
            {
                OnSpeedUpCancelled?.Invoke();
            }
        }
    }
}
