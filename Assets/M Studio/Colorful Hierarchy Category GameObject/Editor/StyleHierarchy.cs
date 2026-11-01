using UnityEditor;
using UnityEngine;
#if UNITY_6000_5_OR_NEWER
using Unity.Hierarchy;
using Unity.Hierarchy.Editor;
using UnityEngine.UIElements;
#endif

namespace MStudio
{
    [InitializeOnLoad]
    public class StyleHierarchy
    {
        private static readonly ColorPalette[] paletteCache = new ColorPalette[1];

        static StyleHierarchy()
        {
            EnsureColorPalette();

#if UNITY_6000_3_OR_NEWER
            EditorApplication.hierarchyWindowItemByEntityIdOnGUI -= OnHierarchyWindow;
            EditorApplication.hierarchyWindowItemByEntityIdOnGUI += OnHierarchyWindow;
#else
            EditorApplication.hierarchyWindowItemOnGUI -= OnHierarchyWindow;
            EditorApplication.hierarchyWindowItemOnGUI += OnHierarchyWindow;
#endif

#if UNITY_6000_5_OR_NEWER
            HierarchyWindow.BindViewItem -= OnBindViewItem;
            HierarchyWindow.BindViewItem += OnBindViewItem;
            EditorApplication.hierarchyChanged -= RefreshNewHierarchyWindows;
            EditorApplication.hierarchyChanged += RefreshNewHierarchyWindows;
            EditorApplication.delayCall += RefreshNewHierarchyWindows;
#endif
        }

        private static ColorPalette EnsureColorPalette()
        {
            if (paletteCache[0] != null) return paletteCache[0];

            string[] dataArray = AssetDatabase.FindAssets("t:ColorPalette");
            if (dataArray != null && dataArray.Length >= 1)
            {
                string path = AssetDatabase.GUIDToAssetPath(dataArray[0]);
                paletteCache[0] = AssetDatabase.LoadAssetAtPath<ColorPalette>(path);
            }

            return paletteCache[0];
        }

        private static ColorDesign FindMatchingDesign(string objectName)
        {
            ColorPalette colorPalette = EnsureColorPalette();
            if (string.IsNullOrEmpty(objectName) || colorPalette == null || colorPalette.colorDesigns == null)
                return null;

            ColorDesign matched = null;
            for (int i = 0; i < colorPalette.colorDesigns.Count; i++)
            {
                var design = colorPalette.colorDesigns[i];
                if (design != null && !string.IsNullOrEmpty(design.keyChar) && objectName.StartsWith(design.keyChar))
                {
                    matched = design;
                }
            }
            return matched;
        }

#if UNITY_6000_3_OR_NEWER
        private static void OnHierarchyWindow(EntityId instanceID, Rect selectionRect)
        {
            if (EnsureColorPalette() == null) return;
            UnityEngine.Object instance = EditorUtility.EntityIdToObject(instanceID);
            DrawIMGUIHierarchyItem(instance, selectionRect);
        }
#else
        private static void OnHierarchyWindow(int instanceID, Rect selectionRect)
        {
            if (EnsureColorPalette() == null) return;
            UnityEngine.Object instance = EditorUtility.InstanceIDToObject(instanceID);
            DrawIMGUIHierarchyItem(instance, selectionRect);
        }
#endif

        private static void DrawIMGUIHierarchyItem(UnityEngine.Object instance, Rect selectionRect)
        {
            if (instance == null) return;

            var design = FindMatchingDesign(instance.name);
            if (design != null)
            {
                //Remove the symbol(keyChar) from the name.
                string newName = instance.name.Substring(design.keyChar.Length);
                //Draw a rectangle as a background, and set the color.
                EditorGUI.DrawRect(selectionRect, design.backgroundColor);

                //Create a new GUIStyle to match the desing in colorDesigns list.
                GUIStyle newStyle = new GUIStyle
                {
                    alignment = design.textAlignment,
                    fontStyle = design.fontStyle,
                    normal = new GUIStyleState()
                    {
                        textColor = design.textColor,
                    }
                };

                //Draw a label to show the name in upper letters and newStyle.
                //If you don't like all capital latter, you can remove ".ToUpper()".
                EditorGUI.LabelField(selectionRect, newName.ToUpper(), newStyle);
            }
        }

#if UNITY_6000_5_OR_NEWER
        private static void OnBindViewItem(HierarchyWindow window, HierarchyView view, HierarchyViewItem item)
        {
            ApplyNewHierarchyItemStyle(item);
        }

        public static void RefreshNewHierarchyWindows()
        {
            var windows = Resources.FindObjectsOfTypeAll<HierarchyWindow>();
            foreach (var window in windows)
            {
                if (window == null || window.rootVisualElement == null) continue;
                window.rootVisualElement.Query<HierarchyViewItem>().ForEach(ApplyNewHierarchyItemStyle);
            }
        }

        private static void ApplyNewHierarchyItemStyle(HierarchyViewItem item)
        {
            if (item == null || item.Name == null) return;

            GameObject instance = null;
            if (item.Handler is HierarchyGameObjectHandler handler)
            {
                instance = handler.GetGameObject(item.Node);
            }

            var design = instance != null ? FindMatchingDesign(instance.name) : null;
            if (design != null)
            {
                string newName = instance.name.Substring(design.keyChar.Length);

                item.style.backgroundColor = design.backgroundColor;
                if (item.Icon != null) item.Icon.style.display = DisplayStyle.None;
                if (item.LeftCustomContainer != null) item.LeftCustomContainer.style.display = DisplayStyle.None;

                item.Name.text = newName.ToUpper();
                item.Name.style.color = design.textColor;
                item.Name.style.unityFontStyleAndWeight = design.fontStyle;
                item.Name.style.unityTextAlign = design.textAlignment;
                item.Name.style.flexGrow = 1f;
            }
            else
            {
                item.style.backgroundColor = StyleKeyword.Null;
                if (item.Icon != null) item.Icon.style.display = StyleKeyword.Null;
                if (item.LeftCustomContainer != null) item.LeftCustomContainer.style.display = StyleKeyword.Null;

                if (instance != null) item.Name.text = instance.name;
                item.Name.style.color = StyleKeyword.Null;
                item.Name.style.unityFontStyleAndWeight = StyleKeyword.Null;
                item.Name.style.unityTextAlign = StyleKeyword.Null;
                item.Name.style.flexGrow = StyleKeyword.Null;
            }
        }
#endif
    }
}
