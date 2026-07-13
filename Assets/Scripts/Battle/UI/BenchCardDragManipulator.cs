using UnityEngine;
using UnityEngine.UIElements;

namespace MagicSchool.Battle
{
    // UI Toolkit replacement for the old uGUI BenchCardDrag (IBeginDragHandler/IDragHandler/
    // IEndDragHandler/IPointerClickHandler). Manually reimplements click-vs-drag disambiguation
    // that uGUI's EventSystem provided for free via its drag threshold.
    public class BenchCardDragManipulator : PointerManipulator
    {
        private const float DragThreshold = 10f; // mirrors old EventSystem.m_DragThreshold: 10

        private readonly BattleBoardManager _owner;
        private readonly string _studentId;
        private Vector2 _pointerDownPos;
        private bool _dragging;
        private int _pointerId = -1;

        public BenchCardDragManipulator(BattleBoardManager owner, string studentId)
        {
            _owner = owner;
            _studentId = studentId;
        }

        protected override void RegisterCallbacksOnTarget()
        {
            target.RegisterCallback<PointerDownEvent>(OnPointerDown);
            target.RegisterCallback<PointerMoveEvent>(OnPointerMove);
            target.RegisterCallback<PointerUpEvent>(OnPointerUp);
            target.RegisterCallback<PointerCaptureOutEvent>(OnPointerCaptureOut);
        }

        protected override void UnregisterCallbacksFromTarget()
        {
            target.UnregisterCallback<PointerDownEvent>(OnPointerDown);
            target.UnregisterCallback<PointerMoveEvent>(OnPointerMove);
            target.UnregisterCallback<PointerUpEvent>(OnPointerUp);
            target.UnregisterCallback<PointerCaptureOutEvent>(OnPointerCaptureOut);
        }

        private void OnPointerDown(PointerDownEvent evt)
        {
            if (evt.button != 0) return; // primary button only
            _pointerId = evt.pointerId;
            _pointerDownPos = evt.position;
            _dragging = false;
            target.CapturePointer(_pointerId);
        }

        private void OnPointerMove(PointerMoveEvent evt)
        {
            if (!target.HasPointerCapture(evt.pointerId)) return;
            var delta = (Vector2)evt.position - _pointerDownPos;
            if (!_dragging && delta.sqrMagnitude > DragThreshold * DragThreshold)
            {
                _dragging = true;
                _owner.OnCardDragStart(_studentId);
            }
            if (_dragging)
                _owner.OnCardDrag(PanelToScreen(evt.position));
        }

        private void OnPointerUp(PointerUpEvent evt)
        {
            if (!target.HasPointerCapture(evt.pointerId)) return;
            target.ReleasePointer(evt.pointerId);
            if (_dragging)
                _owner.OnCardDragEnd(PanelToScreen(evt.position));
            // A click that never crossed the drag threshold does nothing. It used to call
            // _owner.OnCardClicked() → HeroSelection.Select(), which had zero subscribers
            // anywhere — so the click did nothing then either, just less honestly.
            _dragging = false;
        }

        private void OnPointerCaptureOut(PointerCaptureOutEvent evt)
        {
            // Safety net: pointer capture lost unexpectedly (e.g. app lost focus) — cancel any in-flight drag.
            if (_dragging)
                _owner.OnCardDragEnd(PanelToScreen(target.worldBound.center));
            _dragging = false;
        }

        // RuntimePanelUtils only exposes ScreenToPanel (the inverse) in this Unity version, so
        // PanelToScreen is computed manually. Panel space (points) is not guaranteed 1:1 with
        // true screen pixels — BattleHUDPanelSettings uses PanelScaleMode.ConstantPhysicalSize,
        // so any actual DPI other than the configured reference/fallback DPI (96) introduces a
        // non-1:1 scale. target.panel.visualTree always spans the full panel in panel-space
        // units, so comparing its measured layout size to Screen.width/height gives the exact
        // panel-to-screen scale for the current DPI, with no dependency on undocumented
        // UIElements APIs. Unity screen space is Y-up-from-bottom, so Y is also flipped.
        private Vector2 PanelToScreen(Vector2 panelPosition)
        {
            VisualElement panelRoot = target.panel.visualTree;
            float scaleX = Screen.width  / panelRoot.layout.width;
            float scaleY = Screen.height / panelRoot.layout.height;
            return new Vector2(panelPosition.x * scaleX, Screen.height - panelPosition.y * scaleY);
        }
    }
}
