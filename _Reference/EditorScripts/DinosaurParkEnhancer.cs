using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.Animations;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace MiniGame.Editor
{
    public static class DinosaurParkEnhancer
    {
        private const string ScenePath = "Assets/Scenes/DinosaurPark.unity";
        private const string DinoBasePath = "Assets/Models/Dinosaurs";
        private const string CharBasePath = "Assets/Models/Characters";
        private const string EnvModelsPath = "Assets/Models/Environment/Models";
        private const string EnvTexturesPath = "Assets/Models/Environment/Textures";
        private const string EnvMaterialsPath = "Assets/Models/Environment/Materials";
        private const string ParkMaterialsPath = "Assets/Models/Environment/Materials/Park";

        [MenuItem("Tools/MiniGame/Enhance Dinosaur Park (Real Colors, Habits, Player, Wind, Birds, Crowds)")]
        public static void EnhanceParkScene()
        {
            Debug.Log("[DinosaurParkEnhancer] Starting comprehensive park upgrade...");

            // 1. Ensure scene is open
            Scene scene = SceneManager.GetActiveScene();
            if (scene.path != ScenePath)
            {
                scene = EditorSceneManager.OpenScene(ScenePath);
            }

            Shader urpLit = Shader.Find("Universal Render Pipeline/Lit");
            if (urpLit == null)
            {
                Debug.LogError("[DinosaurParkEnhancer] URP Lit shader not found!");
                return;
            }

            EnsureDirectories();

            // 2. Setup Lush Green Foliage Materials (replace red autumn with lush Jurassic greens)
            SetupLushGreenFoliage(urpLit);

            // 3. Create Authentic Dinosaur Materials (Real Colors)
            var dinoMats = CreateRealisticDinoMaterials(urpLit);

            // 4. Create Diverse Visitor Clothing Palette
            var visitorPalette = CreateVisitorClothingPalette(urpLit);

            // 5. Build/Configure Dinosaur Animator Controllers
            var apatCtrl = GetOrBuildDinoController("Apatosaurus", "Armature|Apatosaurus_Idle", "Armature|Apatosaurus_Walk", "Armature|Apatosaurus_Attack");
            var parasaurCtrl = GetOrBuildDinoController("Parasaurolophus", "Armature|Parasaurolophus_Idle", "Armature|Parasaurolophus_Walk", "Armature|Parasaurolophus_Attack");
            var raptorCtrl = GetOrBuildDinoController("Velociraptor", "Armature|Velociraptor_Idle", "Armature|Velociraptor_Walk", "Armature|Velociraptor_Attack");

            // 6. Setup Ground Geometry & Real 3D Grass
            SetupGroundGeometryAndGrass(urpLit);

            // 7. Setup Water Pond with Moving Water & Drinking Spots
            SetupPondAndWater(urpLit);

            // 8. Configure Dinosaurs with Real Colors & Habit AI
            ConfigureDinosaurs(dinoMats, apatCtrl, parasaurCtrl, raptorCtrl);

            // 9. Configure Spectators / Visitors with Dynamic AI & Diverse Clothing
            ConfigureSpectators(visitorPalette);

            // 10. Add Wind Sway to Trees & Bushes across the Map
            SetupTreesAndWindSway(urpLit);

            // 11. Add Soaring Sky Birds
            SetupSkyBirds();

            // 12. Setup Playable Character with Free Roam Controls & Follow Camera
            SetupPlayableCharacter();

            // Save Scene
            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene);
            AssetDatabase.SaveAssets();

            Debug.Log("[DinosaurParkEnhancer] Dinosaur Park successfully enhanced!");
        }

        private static void EnsureDirectories()
        {
            if (!AssetDatabase.IsValidFolder("Assets/Materials"))
                AssetDatabase.CreateFolder("Assets", "Materials");
            if (!AssetDatabase.IsValidFolder("Assets/Materials/Dinosaurs"))
                AssetDatabase.CreateFolder("Assets/Materials", "Dinosaurs");
            if (!AssetDatabase.IsValidFolder("Assets/Materials/Visitors"))
                AssetDatabase.CreateFolder("Assets/Materials", "Visitors");
            if (!AssetDatabase.IsValidFolder("Assets/Animations"))
                AssetDatabase.CreateFolder("Assets", "Animations");
            if (!AssetDatabase.IsValidFolder("Assets/Animations/Dinosaurs"))
                AssetDatabase.CreateFolder("Assets/Animations", "Dinosaurs");
        }

        private static void SetupLushGreenFoliage(Shader urpLit)
        {
            // Update M_Leaves_NormalTree to use green Leaves_NormalTree.png instead of autumn red
            string matPath = $"{EnvMaterialsPath}/M_Leaves_NormalTree.mat";
            Material mat = AssetDatabase.LoadAssetAtPath<Material>(matPath);
            if (mat != null)
            {
                Texture2D greenLeaves = AssetDatabase.LoadAssetAtPath<Texture2D>($"{EnvTexturesPath}/Leaves_NormalTree.png");
                if (greenLeaves != null)
                {
                    mat.SetTexture("_BaseMap", greenLeaves);
                    mat.SetColor("_BaseColor", new Color(0.9f, 1.0f, 0.9f));
                }
                EditorUtility.SetDirty(mat);
            }

            // Update M_Leaves_TwistedTree to use green Leaves_TwistedTree.png
            string matTwistedPath = $"{EnvMaterialsPath}/M_Leaves_TwistedTree.mat";
            Material matTwisted = AssetDatabase.LoadAssetAtPath<Material>(matTwistedPath);
            if (matTwisted != null)
            {
                Texture2D greenTwisted = AssetDatabase.LoadAssetAtPath<Texture2D>($"{EnvTexturesPath}/Leaves_TwistedTree.png");
                if (greenTwisted != null)
                {
                    matTwisted.SetTexture("_BaseMap", greenTwisted);
                    matTwisted.SetColor("_BaseColor", new Color(0.95f, 1.0f, 0.95f));
                }
                EditorUtility.SetDirty(matTwisted);
            }

            // Update M_Pine
            string matPinePath = $"{EnvMaterialsPath}/M_Pine.mat";
            Material matPine = AssetDatabase.LoadAssetAtPath<Material>(matPinePath);
            if (matPine != null)
            {
                Texture2D pineTex = AssetDatabase.LoadAssetAtPath<Texture2D>($"{EnvTexturesPath}/Leaf_Pine.png");
                if (pineTex != null)
                {
                    matPine.SetTexture("_BaseMap", pineTex);
                }
                EditorUtility.SetDirty(matPine);
            }
        }

        private static Dictionary<string, Material[]> CreateRealisticDinoMaterials(Shader urpLit)
        {
            var dict = new Dictionary<string, Material[]>();

            // 1. APATOSAURUS (Slate moss-grey leathery hide + weathered warm tan underbelly)
            var matApatoHide = GetOrCreatePBRMaterial("Assets/Materials/Dinosaurs/M_Apatosaurus_Hide.mat",
                new Color(0.26f, 0.31f, 0.27f), 0.18f, 0.0f, urpLit);
            var matApatoBelly = GetOrCreatePBRMaterial("Assets/Materials/Dinosaurs/M_Apatosaurus_Belly.mat",
                new Color(0.44f, 0.42f, 0.35f), 0.15f, 0.0f, urpLit);
            dict["Apatosaurus"] = new Material[] { matApatoHide, matApatoBelly };

            // 2. PARASAUROLOPHUS (Rich olive body, soft sand belly, sage stripes, striking coral crest)
            var matParasaurBelly = GetOrCreatePBRMaterial("Assets/Materials/Dinosaurs/M_Parasaur_Belly.mat",
                new Color(0.78f, 0.74f, 0.58f), 0.16f, 0.0f, urpLit);
            var matParasaurDorsal = GetOrCreatePBRMaterial("Assets/Materials/Dinosaurs/M_Parasaur_Dorsal.mat",
                new Color(0.24f, 0.32f, 0.18f), 0.22f, 0.0f, urpLit);
            var matParasaurStripes = GetOrCreatePBRMaterial("Assets/Materials/Dinosaurs/M_Parasaur_Stripes.mat",
                new Color(0.42f, 0.52f, 0.28f), 0.20f, 0.0f, urpLit);
            var matParasaurCrest = GetOrCreatePBRMaterial("Assets/Materials/Dinosaurs/M_Parasaur_Crest.mat",
                new Color(0.64f, 0.20f, 0.14f), 0.35f, 0.0f, urpLit);
            dict["Parasaurolophus"] = new Material[] { matParasaurBelly, matParasaurDorsal, matParasaurStripes, matParasaurCrest };

            // 3. VELOCIRAPTOR (Predator tiger camo: pale sand belly, warm umber mottled hide, glossy black claws)
            var matRaptorBelly = GetOrCreatePBRMaterial("Assets/Materials/Dinosaurs/M_Raptor_Belly.mat",
                new Color(0.72f, 0.66f, 0.54f), 0.18f, 0.0f, urpLit);
            var matRaptorHide = GetOrCreatePBRMaterial("Assets/Materials/Dinosaurs/M_Raptor_Hide.mat",
                new Color(0.36f, 0.28f, 0.18f), 0.25f, 0.0f, urpLit);
            var matRaptorClaws = GetOrCreatePBRMaterial("Assets/Materials/Dinosaurs/M_Raptor_Claws.mat",
                new Color(0.10f, 0.09f, 0.08f), 0.55f, 0.1f, urpLit);
            dict["Velociraptor"] = new Material[] { matRaptorBelly, matRaptorHide, matRaptorClaws };

            return dict;
        }

        private static (Material[] skins, Material[] shirts, Material[] pants, Material[] shoes, Material[] hair) CreateVisitorClothingPalette(Shader urpLit)
        {
            // Diverse skin tones
            var skins = new Material[]
            {
                GetOrCreatePBRMaterial("Assets/Materials/Visitors/M_Skin_Light.mat", new Color(0.92f, 0.78f, 0.68f), 0.2f, 0f, urpLit),
                GetOrCreatePBRMaterial("Assets/Materials/Visitors/M_Skin_Tan.mat", new Color(0.82f, 0.65f, 0.50f), 0.2f, 0f, urpLit),
                GetOrCreatePBRMaterial("Assets/Materials/Visitors/M_Skin_WarmBrown.mat", new Color(0.55f, 0.38f, 0.26f), 0.2f, 0f, urpLit),
                GetOrCreatePBRMaterial("Assets/Materials/Visitors/M_Skin_Deep.mat", new Color(0.35f, 0.23f, 0.16f), 0.2f, 0f, urpLit)
            };

            // Stylish shirt colors
            var shirts = new Material[]
            {
                GetOrCreatePBRMaterial("Assets/Materials/Visitors/M_Shirt_Navy.mat", new Color(0.12f, 0.22f, 0.42f), 0.1f, 0f, urpLit),
                GetOrCreatePBRMaterial("Assets/Materials/Visitors/M_Shirt_Burgundy.mat", new Color(0.48f, 0.14f, 0.18f), 0.1f, 0f, urpLit),
                GetOrCreatePBRMaterial("Assets/Materials/Visitors/M_Shirt_ForestGreen.mat", new Color(0.18f, 0.38f, 0.22f), 0.1f, 0f, urpLit),
                GetOrCreatePBRMaterial("Assets/Materials/Visitors/M_Shirt_Coral.mat", new Color(0.85f, 0.40f, 0.30f), 0.1f, 0f, urpLit),
                GetOrCreatePBRMaterial("Assets/Materials/Visitors/M_Shirt_Mustard.mat", new Color(0.85f, 0.68f, 0.20f), 0.1f, 0f, urpLit),
                GetOrCreatePBRMaterial("Assets/Materials/Visitors/M_Shirt_Teal.mat", new Color(0.15f, 0.48f, 0.48f), 0.1f, 0f, urpLit),
                GetOrCreatePBRMaterial("Assets/Materials/Visitors/M_Shirt_White.mat", new Color(0.92f, 0.92f, 0.94f), 0.1f, 0f, urpLit),
                GetOrCreatePBRMaterial("Assets/Materials/Visitors/M_Shirt_Charcoal.mat", new Color(0.22f, 0.24f, 0.26f), 0.1f, 0f, urpLit)
            };

            // Pants colors
            var pants = new Material[]
            {
                GetOrCreatePBRMaterial("Assets/Materials/Visitors/M_Pants_Denim.mat", new Color(0.18f, 0.28f, 0.45f), 0.1f, 0f, urpLit),
                GetOrCreatePBRMaterial("Assets/Materials/Visitors/M_Pants_Khaki.mat", new Color(0.68f, 0.60f, 0.48f), 0.1f, 0f, urpLit),
                GetOrCreatePBRMaterial("Assets/Materials/Visitors/M_Pants_DarkGrey.mat", new Color(0.22f, 0.23f, 0.25f), 0.1f, 0f, urpLit),
                GetOrCreatePBRMaterial("Assets/Materials/Visitors/M_Pants_Black.mat", new Color(0.12f, 0.12f, 0.14f), 0.1f, 0f, urpLit)
            };

            // Shoes colors
            var shoes = new Material[]
            {
                GetOrCreatePBRMaterial("Assets/Materials/Visitors/M_Shoes_White.mat", new Color(0.92f, 0.92f, 0.92f), 0.25f, 0f, urpLit),
                GetOrCreatePBRMaterial("Assets/Materials/Visitors/M_Shoes_Brown.mat", new Color(0.35f, 0.22f, 0.14f), 0.3f, 0f, urpLit),
                GetOrCreatePBRMaterial("Assets/Materials/Visitors/M_Shoes_Black.mat", new Color(0.14f, 0.14f, 0.15f), 0.3f, 0f, urpLit)
            };

            // Hair colors
            var hair = new Material[]
            {
                GetOrCreatePBRMaterial("Assets/Materials/Visitors/M_Hair_DarkBrown.mat", new Color(0.20f, 0.14f, 0.10f), 0.35f, 0f, urpLit),
                GetOrCreatePBRMaterial("Assets/Materials/Visitors/M_Hair_Black.mat", new Color(0.08f, 0.08f, 0.09f), 0.4f, 0f, urpLit),
                GetOrCreatePBRMaterial("Assets/Materials/Visitors/M_Hair_Blonde.mat", new Color(0.82f, 0.70f, 0.42f), 0.35f, 0f, urpLit),
                GetOrCreatePBRMaterial("Assets/Materials/Visitors/M_Hair_Auburn.mat", new Color(0.48f, 0.22f, 0.14f), 0.35f, 0f, urpLit)
            };

            return (skins, shirts, pants, shoes, hair);
        }

        private static AnimatorController GetOrBuildDinoController(string speciesName, string idleClipName, string walkClipName, string attackClipName)
        {
            string path = $"Assets/Animations/Dinosaurs/{speciesName}_Controller.controller";
            var ctrl = AssetDatabase.LoadAssetAtPath<AnimatorController>(path);
            if (ctrl == null)
            {
                ctrl = AnimatorController.CreateAnimatorControllerAtPath(path);

                // Add Parameters
                ctrl.AddParameter("Speed", AnimatorControllerParameterType.Float);
                ctrl.AddParameter("Action", AnimatorControllerParameterType.Bool);
                ctrl.AddParameter("Drinking", AnimatorControllerParameterType.Bool);

                // Find Clips
                string fbxPath = $"{DinoBasePath}/{speciesName}.fbx";
                var assets = AssetDatabase.LoadAllAssetsAtPath(fbxPath);
                AnimationClip idleClip = null, walkClip = null, attackClip = null;

                foreach (var a in assets)
                {
                    if (a is AnimationClip clip && !clip.name.StartsWith("__preview__"))
                    {
                        if (clip.name == idleClipName || clip.name.Contains("Idle")) idleClip = clip;
                        else if (clip.name == walkClipName || clip.name.Contains("Walk")) walkClip = clip;
                        else if (clip.name == attackClipName || clip.name.Contains("Attack")) attackClip = clip;
                    }
                }

                var rootStateMachine = ctrl.layers[0].stateMachine;

                // Idle State (Default)
                var idleState = rootStateMachine.AddState("Idle");
                idleState.motion = idleClip;

                // Walk State
                var walkState = rootStateMachine.AddState("Walk");
                walkState.motion = walkClip != null ? walkClip : idleClip;

                // Action / Drink State
                var actionState = rootStateMachine.AddState("Action");
                actionState.motion = attackClip != null ? attackClip : idleClip;

                // Transitions: Idle <-> Walk based on Speed
                var toWalk = idleState.AddTransition(walkState);
                toWalk.AddCondition(AnimatorConditionMode.Greater, 0.1f, "Speed");
                toWalk.duration = 0.25f;

                var toIdle = walkState.AddTransition(idleState);
                toIdle.AddCondition(AnimatorConditionMode.Less, 0.1f, "Speed");
                toIdle.duration = 0.25f;

                // Transitions to Action
                var toActionFromIdle = idleState.AddTransition(actionState);
                toActionFromIdle.AddCondition(AnimatorConditionMode.If, 0, "Action");
                toActionFromIdle.duration = 0.2f;

                var toActionFromWalk = walkState.AddTransition(actionState);
                toActionFromWalk.AddCondition(AnimatorConditionMode.If, 0, "Action");
                toActionFromWalk.duration = 0.2f;

                var backFromAction = actionState.AddTransition(idleState);
                backFromAction.AddCondition(AnimatorConditionMode.IfNot, 0, "Action");
                backFromAction.duration = 0.3f;

                EditorUtility.SetDirty(ctrl);
            }
            return ctrl;
        }

        private static void SetupGroundGeometryAndGrass(Shader urpLit)
        {
            var catGround = GameObject.Find("=== Ground & Terrain ===");
            if (catGround == null) catGround = new GameObject("=== Ground & Terrain ===");

            // Lush stylized grass ground material
            Material matGrass = GetOrCreatePBRMaterial("Assets/Models/Environment/Materials/Park/M_Park_LushGrass.mat",
                new Color(0.24f, 0.48f, 0.18f), 0.05f, 0.0f, urpLit);

            // Check if contoured ground geometry already exists
            Transform hillsGroup = catGround.transform.Find("Natural Ground Undulations");
            if (hillsGroup == null)
            {
                var hObj = new GameObject("Natural Ground Undulations");
                hObj.transform.SetParent(catGround.transform);
                hillsGroup = hObj.transform;

                // Perimeter earthen mounds & hills giving the park depth and natural contours
                CreateGroundMound(hillsGroup, new Vector3(-38f, -0.4f, 32f), new Vector3(18f, 3.2f, 50f), matGrass);
                CreateGroundMound(hillsGroup, new Vector3(38f, -0.4f, 32f), new Vector3(18f, 3.2f, 50f), matGrass);
                CreateGroundMound(hillsGroup, new Vector3(0f, -0.4f, 68f), new Vector3(75f, 3.8f, 22f), matGrass);
                CreateGroundMound(hillsGroup, new Vector3(-18f, -0.3f, 48f), new Vector3(14f, 2.0f, 16f), matGrass);
                CreateGroundMound(hillsGroup, new Vector3(22f, -0.3f, 22f), new Vector3(16f, 1.8f, 18f), matGrass);
                CreateGroundMound(hillsGroup, new Vector3(0f, -0.2f, -22f), new Vector3(35f, 1.2f, 25f), matGrass);
            }

            // Real 3D Grass Clumps scattering
            Transform grassGroup = catGround.transform.Find("Volumetric 3D Grass Clumps");
            if (grassGroup == null)
            {
                var gObj = new GameObject("Volumetric 3D Grass Clumps");
                gObj.transform.SetParent(catGround.transform);
                grassGroup = gObj.transform;

                string grassModel = $"{EnvModelsPath}/Grass.fbx";
                string fernModel = $"{EnvModelsPath}/Fern_1.fbx";
                string flowersModel = $"{EnvModelsPath}/Flower_3_Group.fbx";

                GameObject grassAsset = AssetDatabase.LoadAssetAtPath<GameObject>(grassModel);
                GameObject fernAsset = AssetDatabase.LoadAssetAtPath<GameObject>(fernModel);
                GameObject flowerAsset = AssetDatabase.LoadAssetAtPath<GameObject>(flowersModel);

                // Scatter inside paddock and around paths
                ScatterFoliageClumps(grassGroup, grassAsset, 65, new Rect(-32f, 4f, 64f, 54f), 1.2f, 2.4f);
                ScatterFoliageClumps(grassGroup, fernAsset, 35, new Rect(-30f, 6f, 60f, 52f), 1.0f, 1.8f);
                ScatterFoliageClumps(grassGroup, flowerAsset, 22, new Rect(-28f, 8f, 56f, 48f), 0.9f, 1.5f);

                // Scatter around plaza / outside fence
                ScatterFoliageClumps(grassGroup, grassAsset, 45, new Rect(-25f, -38f, 50f, 32f), 1.1f, 2.2f);
                ScatterFoliageClumps(grassGroup, flowerAsset, 16, new Rect(-20f, -35f, 40f, 28f), 0.9f, 1.4f);
            }
        }

        private static void CreateGroundMound(Transform parent, Vector3 pos, Vector3 scale, Material mat)
        {
            GameObject mound = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            mound.name = "Earthen Terrain Contour";
            mound.transform.SetParent(parent);
            mound.transform.position = pos;
            mound.transform.localScale = scale;
            mound.GetComponent<Renderer>().sharedMaterial = mat;
        }

        private static void ScatterFoliageClumps(Transform parent, GameObject asset, int count, Rect area, float minScale, float maxScale)
        {
            if (asset == null) return;
            for (int i = 0; i < count; i++)
            {
                float x = Random.Range(area.xMin, area.xMax);
                float z = Random.Range(area.yMin, area.yMax);
                GameObject clump = PrefabUtility.InstantiatePrefab(asset) as GameObject;
                clump.transform.SetParent(parent);
                clump.transform.position = new Vector3(x, 0.05f, z);
                clump.transform.rotation = Quaternion.Euler(0, Random.Range(0f, 360f), 0);
                clump.transform.localScale = Vector3.one * Random.Range(minScale, maxScale);

                // Add subtle wind sway to grass & ferns
                clump.AddComponent<FoliageWindSway>();
            }
        }

        private static void SetupPondAndWater(Shader urpLit)
        {
            var catEnclosure = GameObject.Find("=== Dinosaurs (Enclosure) ===");
            if (catEnclosure == null) catEnclosure = new GameObject("=== Dinosaurs (Enclosure) ===");

            Transform pondRoot = catEnclosure.transform.Find("Dinosaur Water Pond");
            if (pondRoot != null) return; // already created

            GameObject pondObj = new GameObject("Dinosaur Water Pond");
            pondObj.transform.SetParent(catEnclosure.transform);
            pondObj.transform.position = new Vector3(6f, 0.08f, 30f); // centered naturally in paddock

            // Animated water material
            Material matWater = GetOrCreatePBRMaterial("Assets/Materials/M_Park_Water.mat",
                new Color(0.18f, 0.58f, 0.65f, 0.88f), 0.92f, 0.05f, urpLit);

            // Pond Water Surface
            GameObject waterPlane = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            waterPlane.name = "Water Surface";
            waterPlane.transform.SetParent(pondObj.transform);
            waterPlane.transform.localPosition = Vector3.zero;
            waterPlane.transform.localScale = new Vector3(14f, 0.1f, 10f); // 14m x 10m pond
            waterPlane.GetComponent<Renderer>().sharedMaterial = matWater;

            // Pond Water Component for ripples and drinking
            var pondWater = waterPlane.AddComponent<PondWater>();

            // Recessed Basin Shoreline (pebble/mud embankment)
            Material matBasin = GetOrCreatePBRMaterial("Assets/Models/Environment/Materials/Park/M_Park_AsphaltPath.mat",
                new Color(0.38f, 0.32f, 0.24f), 0.1f, 0f, urpLit);

            GameObject basin = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            basin.name = "Pond Earthen Basin";
            basin.transform.SetParent(pondObj.transform);
            basin.transform.localPosition = new Vector3(0f, -0.06f, 0f);
            basin.transform.localScale = new Vector3(15.5f, 0.1f, 11.5f);
            basin.GetComponent<Renderer>().sharedMaterial = matBasin;

            // Drinking Spots around pond shoreline
            Vector3[] spots = new Vector3[]
            {
                new Vector3(-6.2f, 0f, 0f),
                new Vector3(6.2f, 0f, 0f),
                new Vector3(0f, 0f, 4.8f),
                new Vector3(0f, 0f, -4.8f),
                new Vector3(-4.5f, 0f, 3.2f),
                new Vector3(4.5f, 0f, -3.2f)
            };

            for (int s = 0; s < spots.Length; s++)
            {
                GameObject spot = new GameObject($"DrinkSpot_{s + 1}");
                spot.transform.SetParent(pondObj.transform);
                spot.transform.localPosition = spots[s];
            }

            // River rocks framing the pond
            string rockPrefab = $"{EnvModelsPath}/Rock_Medium_1.fbx";
            GameObject rockAsset = AssetDatabase.LoadAssetAtPath<GameObject>(rockPrefab);
            if (rockAsset != null)
            {
                for (int r = 0; r < 6; r++)
                {
                    float angle = r * 60f * Mathf.Deg2Rad;
                    Vector3 rPos = new Vector3(Mathf.Cos(angle) * 7.5f, 0f, Mathf.Sin(angle) * 5.6f);
                    GameObject rock = PrefabUtility.InstantiatePrefab(rockAsset) as GameObject;
                    rock.transform.SetParent(pondObj.transform);
                    rock.transform.localPosition = rPos;
                    rock.transform.localScale = Vector3.one * Random.Range(1.0f, 1.8f);
                    rock.transform.localRotation = Quaternion.Euler(0, Random.Range(0, 360f), 0);
                }
            }
        }

        private static void ConfigureDinosaurs(Dictionary<string, Material[]> mats,
            AnimatorController apatCtrl, AnimatorController parasaurCtrl, AnimatorController raptorCtrl)
        {
            var dinoRoot = GameObject.Find("=== Dinosaurs (Enclosure) ===");
            if (dinoRoot == null) return;

            for (int i = 0; i < dinoRoot.transform.childCount; i++)
            {
                var child = dinoRoot.transform.GetChild(i);
                string name = child.name;

                SkinnedMeshRenderer smr = child.GetComponentInChildren<SkinnedMeshRenderer>();
                Animator anim = child.GetComponent<Animator>();
                if (anim == null) anim = child.gameObject.AddComponent<Animator>();

                var ai = child.GetComponent<DinosaurHabitAI>();
                if (ai == null) ai = child.gameObject.AddComponent<DinosaurHabitAI>();

                if (name.Contains("Apatosaurus"))
                {
                    ai.SetSpecies(DinoSpecies.Apatosaurus);
                    anim.runtimeAnimatorController = apatCtrl;
                    if (smr != null && mats.ContainsKey("Apatosaurus"))
                        smr.sharedMaterials = mats["Apatosaurus"];
                }
                else if (name.Contains("Parasaurolophus"))
                {
                    ai.SetSpecies(DinoSpecies.Parasaurolophus);
                    anim.runtimeAnimatorController = parasaurCtrl;
                    if (smr != null && mats.ContainsKey("Parasaurolophus"))
                        smr.sharedMaterials = mats["Parasaurolophus"];
                }
                else if (name.Contains("Velociraptor"))
                {
                    ai.SetSpecies(DinoSpecies.Velociraptor);
                    anim.runtimeAnimatorController = raptorCtrl;
                    if (smr != null && mats.ContainsKey("Velociraptor"))
                        smr.sharedMaterials = mats["Velociraptor"];
                }
            }
        }

        private static void ConfigureSpectators((Material[] skins, Material[] shirts, Material[] pants, Material[] shoes, Material[] hair) palette)
        {
            // Gather all visitor game objects
            var visitors = new List<GameObject>();

            var catVisitors = GameObject.Find("=== Visitors (Background Characters) ===");
            if (catVisitors != null)
            {
                for (int i = 0; i < catVisitors.transform.childCount; i++)
                    visitors.Add(catVisitors.transform.GetChild(i).gameObject);
            }

            // Also find any loose visitor objects in scene
            var allObjs = SceneManager.GetActiveScene().GetRootGameObjects();
            foreach (var obj in allObjs)
            {
                string n = obj.name;
                if ((n.StartsWith("Female_") || n.StartsWith("Male_") || n.StartsWith("Woman_")) && !visitors.Contains(obj))
                {
                    if (catVisitors != null) obj.transform.SetParent(catVisitors.transform);
                    visitors.Add(obj);
                }
            }

            int index = 0;
            foreach (var vis in visitors)
            {
                // 1. Assign stylish randomized clothing materials to all 4 submeshes
                var smr = vis.GetComponentInChildren<SkinnedMeshRenderer>();
                if (smr != null && smr.sharedMesh != null && smr.sharedMesh.subMeshCount >= 4)
                {
                    var chosenSkin = palette.skins[index % palette.skins.Length];
                    var chosenShirt = palette.shirts[index % palette.shirts.Length];
                    var chosenPants = palette.pants[(index * 2) % palette.pants.Length];
                    var chosenShoes = palette.shoes[(index * 3) % palette.shoes.Length];

                    smr.sharedMaterials = new Material[] { chosenSkin, chosenShirt, chosenPants, chosenShoes };
                }

                // 2. Assign hair color to hair mesh
                foreach (var mr in vis.GetComponentsInChildren<MeshRenderer>())
                {
                    if (mr.gameObject != vis && mr.gameObject.name.Contains("Hairstyle"))
                    {
                        var chosenHair = palette.hair[(index * 2) % palette.hair.Length];
                        mr.sharedMaterial = chosenHair;
                    }
                }

                // 3. Attach & Configure VisitorAI
                var ai = vis.GetComponent<VisitorAI>();
                if (ai == null) ai = vis.AddComponent<VisitorAI>();

                index++;
            }
        }

        private static void SetupTreesAndWindSway(Shader urpLit)
        {
            var catFoliage = GameObject.Find("=== Environment & Vegetation ===");
            if (catFoliage == null) catFoliage = new GameObject("=== Environment & Vegetation ===");

            // Attach FoliageWindSway to all existing trees & plants
            foreach (Transform child in catFoliage.transform)
            {
                if (child.GetComponent<FoliageWindSway>() == null)
                {
                    child.gameObject.AddComponent<FoliageWindSway>();
                }
            }

            // Check if additional forest groves already exist
            Transform additionalForest = catFoliage.transform.Find("Extended Park Forest");
            if (additionalForest != null) return;

            GameObject forestRoot = new GameObject("Extended Park Forest");
            forestRoot.transform.SetParent(catFoliage.transform);

            string[] treeModels = new string[]
            {
                "TwistedTree_1.fbx", "TwistedTree_3.fbx", "CommonTree_1.fbx", "CommonTree_2.fbx", "Pine_1.fbx", "Pine_3.fbx"
            };

            // 1. Avenue Groves flanking both sides of the Visitor Road (Z = -45 to -15)
            for (float z = -45f; z <= -12f; z += 6f)
            {
                SpawnWindTree(treeModels[Random.Range(0, treeModels.Length)], forestRoot.transform, new Vector3(-8f + Random.Range(-2f, 2f), 0, z), Random.Range(1.4f, 2.2f));
                SpawnWindTree(treeModels[Random.Range(0, treeModels.Length)], forestRoot.transform, new Vector3(8f + Random.Range(-2f, 2f), 0, z), Random.Range(1.4f, 2.2f));
            }

            // 2. Forest Groves along Left & Right Flanks (X = -42 to -28, and X = 28 to 42)
            for (float z = -25f; z <= 60f; z += 9f)
            {
                SpawnWindTree(treeModels[Random.Range(0, treeModels.Length)], forestRoot.transform, new Vector3(-35f + Random.Range(-4f, 4f), 0, z), Random.Range(1.5f, 2.4f));
                SpawnWindTree(treeModels[Random.Range(0, treeModels.Length)], forestRoot.transform, new Vector3(35f + Random.Range(-4f, 4f), 0, z), Random.Range(1.5f, 2.4f));
            }

            // 3. Paddock Shade Groves (inside enclosure near corners and pond)
            SpawnWindTree("TwistedTree_3.fbx", forestRoot.transform, new Vector3(-20f, 0, 18f), 2.2f);
            SpawnWindTree("CommonTree_1.fbx", forestRoot.transform, new Vector3(-24f, 0, 48f), 2.5f);
            SpawnWindTree("Pine_3.fbx", forestRoot.transform, new Vector3(20f, 0, 48f), 2.6f);
            SpawnWindTree("TwistedTree_1.fbx", forestRoot.transform, new Vector3(18f, 0, 26f), 2.0f);
        }

        private static void SpawnWindTree(string fbxName, Transform parent, Vector3 pos, float scale)
        {
            string path = $"{EnvModelsPath}/{fbxName}";
            GameObject asset = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if (asset == null) return;

            GameObject prop = PrefabUtility.InstantiatePrefab(asset) as GameObject;
            prop.name = Path.GetFileNameWithoutExtension(fbxName);
            prop.transform.SetParent(parent);
            prop.transform.position = pos;
            prop.transform.rotation = Quaternion.Euler(0, Random.Range(0, 360f), 0);
            prop.transform.localScale = Vector3.one * scale;

            // Apply lush materials
            ApplyFoliageMaterials(prop, fbxName);

            // Add wind sway
            prop.AddComponent<FoliageWindSway>();
        }

        private static void ApplyFoliageMaterials(GameObject prop, string fbxName)
        {
            foreach (Renderer rend in prop.GetComponentsInChildren<Renderer>())
            {
                if (rend == null) continue;

                if (fbxName.Contains("TwistedTree"))
                {
                    Material bark = AssetDatabase.LoadAssetAtPath<Material>($"{EnvMaterialsPath}/M_Bark_TwistedTree.mat");
                    Material leaves = AssetDatabase.LoadAssetAtPath<Material>($"{EnvMaterialsPath}/M_Leaves_TwistedTree.mat");
                    if (bark != null && leaves != null)
                        rend.sharedMaterials = rend.sharedMaterials.Length >= 2 ? new Material[] { bark, leaves } : new Material[] { leaves };
                }
                else if (fbxName.Contains("CommonTree"))
                {
                    Material bark = AssetDatabase.LoadAssetAtPath<Material>($"{EnvMaterialsPath}/M_Bark_NormalTree.mat");
                    Material leaves = AssetDatabase.LoadAssetAtPath<Material>($"{EnvMaterialsPath}/M_Leaves_NormalTree.mat");
                    if (bark != null && leaves != null)
                        rend.sharedMaterials = rend.sharedMaterials.Length >= 2 ? new Material[] { bark, leaves } : new Material[] { leaves };
                }
                else if (fbxName.Contains("Pine"))
                {
                    Material bark = AssetDatabase.LoadAssetAtPath<Material>($"{EnvMaterialsPath}/M_Bark_NormalTree.mat");
                    Material leaves = AssetDatabase.LoadAssetAtPath<Material>($"{EnvMaterialsPath}/M_Pine.mat");
                    if (bark != null && leaves != null)
                        rend.sharedMaterials = rend.sharedMaterials.Length >= 2 ? new Material[] { bark, leaves } : new Material[] { leaves };
                }
            }
        }

        private static void SetupSkyBirds()
        {
            var catLighting = GameObject.Find("=== Lighting & Atmosphere ===");
            if (catLighting == null) catLighting = new GameObject("=== Lighting & Atmosphere ===");

            if (catLighting.transform.Find("Ambient Sky Birds") == null)
            {
                GameObject birdSystemObj = new GameObject("Ambient Sky Birds");
                birdSystemObj.transform.SetParent(catLighting.transform);
                birdSystemObj.AddComponent<AmbientBirdSystem>();
            }
        }

        private static void SetupPlayableCharacter()
        {
            var catViewpoint = GameObject.Find("=== Observation Deck & Road ===");
            if (catViewpoint == null) catViewpoint = new GameObject("=== Observation Deck & Road ===");

            // Find or keep cinematic deck camera
            GameObject deckCam = GameObject.Find("Main Camera");

            // Check if player already instantiated
            GameObject existingPlayer = GameObject.Find("PlayerArmature");
            if (existingPlayer == null)
            {
                string playerPrefabPath = "Assets/Starter Assets/Runtime/ThirdPersonController/Prefabs/PlayerArmature.prefab";
                GameObject playerPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(playerPrefabPath);
                if (playerPrefab != null)
                {
                    existingPlayer = PrefabUtility.InstantiatePrefab(playerPrefab) as GameObject;
                    existingPlayer.name = "PlayerArmature";
                    existingPlayer.transform.SetParent(catViewpoint.transform);
                    // Spawn at entrance walkway facing toward gate and deck
                    existingPlayer.transform.position = new Vector3(0f, 0.1f, -38f);
                    existingPlayer.transform.rotation = Quaternion.identity;
                }
            }

            // Setup Follow Camera
            GameObject followCam = GameObject.Find("PlayerFollowCamera");
            if (followCam == null)
            {
                string camPrefabPath = "Assets/Starter Assets/Runtime/ThirdPersonController/Prefabs/PlayerFollowCamera.prefab";
                GameObject camPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(camPrefabPath);
                if (camPrefab != null)
                {
                    followCam = PrefabUtility.InstantiatePrefab(camPrefab) as GameObject;
                    followCam.name = "PlayerFollowCamera";
                    followCam.transform.SetParent(catViewpoint.transform);

                    // Hook target to player
                    if (existingPlayer != null)
                    {
                        var camRoot = existingPlayer.transform.Find("PlayerCameraRoot");
                        if (camRoot != null)
                        {
                            var cinemachineCam = followCam.GetComponent<Unity.Cinemachine.CinemachineCamera>();
                            if (cinemachineCam != null)
                            {
                                cinemachineCam.Target.TrackingTarget = camRoot;
                            }
                        }
                    }
                }
            }

            // Ensure Main Camera has CinemachineBrain
            if (deckCam != null)
            {
                if (deckCam.GetComponent<Unity.Cinemachine.CinemachineBrain>() == null)
                {
                    deckCam.AddComponent<Unity.Cinemachine.CinemachineBrain>();
                }

                // Add HUD component to camera or player
                if (deckCam.GetComponent<PlayerRoamHUD>() == null)
                {
                    var hud = deckCam.AddComponent<PlayerRoamHUD>();
                    // Set serialized fields via SerializedObject
                    var so = new SerializedObject(hud);
                    so.FindProperty("playerFollowCamera").objectReferenceValue = followCam;
                    so.FindProperty("cinematicDeckCamera").objectReferenceValue = deckCam;
                    so.ApplyModifiedProperties();
                }
            }
        }

        private static Material GetOrCreatePBRMaterial(string path, Color baseColor, float smoothness, float metallic, Shader shader)
        {
            Material mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null)
            {
                mat = new Material(shader);
                mat.SetColor("_BaseColor", baseColor);
                mat.SetFloat("_Smoothness", smoothness);
                mat.SetFloat("_Metallic", metallic);
                AssetDatabase.CreateAsset(mat, path);
            }
            else
            {
                mat.shader = shader;
                mat.SetColor("_BaseColor", baseColor);
                mat.SetFloat("_Smoothness", smoothness);
                mat.SetFloat("_Metallic", metallic);
                EditorUtility.SetDirty(mat);
            }
            return mat;
        }
    }
}
