using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

// One-shot editor helper: saves the currently open scene IN PLACE.
// coplay's save_scene tool writes Assets/<name>.unity at the project root instead of saving the
// open scene where it lives, so scene saves go through EditorSceneManager directly.
public static class SaveOpenScene
{
    public static void Execute()
    {
        var scene = EditorSceneManager.GetActiveScene();
        bool ok = EditorSceneManager.SaveScene(scene);
        AssetDatabase.SaveAssets();
        Debug.Log(ok
            ? $"[SaveOpenScene] Saved '{scene.name}' in place at {scene.path}"
            : $"[SaveOpenScene] FAILED to save '{scene.name}'");
    }
}
