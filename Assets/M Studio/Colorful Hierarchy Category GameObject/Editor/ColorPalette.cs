using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace MStudio
{
    /// <summary>
    /// Details of custom design
    /// </summary>
    [System.Serializable]
    public class ColorDesign
    {
        [Tooltip("Rename gameObject begin with this keychar")]
        public string keyChar;
        [Tooltip("Don't forget to change alpha to 255")]
        public Color textColor;
        [Tooltip("Don't forget to change alpha to 255")]
        public Color backgroundColor;
        public TextAnchor textAlignment;
        public FontStyle fontStyle;
    }

    /// <summary>
    /// ScriptableObject:Save list of ColorDesign
    /// </summary>
    public class ColorPalette : ScriptableObject
    {
        public List<ColorDesign> colorDesigns = new List<ColorDesign>();

        private void OnValidate()
        {
            EditorApplication.RepaintHierarchyWindow();
#if UNITY_6000_5_OR_NEWER
            StyleHierarchy.RefreshNewHierarchyWindows();
#endif
        }
    }
}
