using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace MiniGame.Editor
{
    public static class DinosaurParkBuilder
    {
        private const string ScenePath = "Assets/Scenes/DinosaurPark.unity";
        private const string DinoBasePath = "Assets/Models/Dinosaurs";
        private const string CharBasePath = "Assets/Models/Characters";
        private const string EnvModelsPath = "Assets/Models/Environment/Models";
        private const string EnvMaterialsPath = "Assets/Models/Environment/Materials";
        private const string ParkMaterialsPath = "Assets/Models/Environment/Materials/Park";

        [MenuItem("Tools/MiniGame/Build Dinosaur Park Scene")]
        public static void BuildParkScene()
        {
            Debug.Log("[DinosaurParkBuilder] Starting Dinosaur Park build...");

            // 1. Target active scene
            Scene scene = SceneManager.GetActiveScene();

            // Clear any existing root objects in scene
            var rootObjects = scene.GetRootGameObjects();
            for (int r = rootObjects.Length - 1; r >= 0; r--)
            {
                Object.DestroyImmediate(rootObjects[r]);
            }

            // Ensure materials folder exists
            if (!AssetDatabase.IsValidFolder(ParkMaterialsPath))
            {
                if (!AssetDatabase.IsValidFolder("Assets/Models/Environment/Materials"))
                    AssetDatabase.CreateFolder("Assets/Models/Environment", "Materials");
                AssetDatabase.CreateFolder("Assets/Models/Environment/Materials", "Park");
            }

            Shader urpLit = Shader.Find("Universal Render Pipeline/Lit");
            if (urpLit == null)
            {
                Debug.LogError("[DinosaurParkBuilder] 'Universal Render Pipeline/Lit' shader not found!");
                return;
            }

            // Create custom park materials
            var matConcrete = GetOrCreateMaterial("M_Park_Concrete", new Color(0.55f, 0.55f, 0.57f), 0.1f, 0.0f, urpLit);
            var matSteel = GetOrCreateMaterial("M_Park_Steel", new Color(0.2f, 0.22f, 0.25f), 0.7f, 0.85f, urpLit);
            var matCable = GetOrCreateMaterial("M_Park_Cable", new Color(0.12f, 0.12f, 0.14f), 0.8f, 0.9f, urpLit);
            var matHazard = GetOrCreateMaterial("M_Park_HazardYellow", new Color(0.95f, 0.75f, 0.05f), 0.3f, 0.1f, urpLit);
            var matDanger = GetOrCreateMaterial("M_Park_DangerRed", new Color(0.85f, 0.12f, 0.12f), 0.4f, 0.1f, urpLit);
            var matWood = GetOrCreateMaterial("M_Park_WoodDeck", new Color(0.58f, 0.38f, 0.22f), 0.15f, 0.0f, urpLit);
            var matRoad = GetOrCreateMaterial("M_Park_AsphaltPath", new Color(0.28f, 0.29f, 0.30f), 0.1f, 0.0f, urpLit);

            // Dinosaur palette materials
            var matDinoGreen = GetOrCreateMaterial("M_Dino_Green", new Color(0.22f, 0.42f, 0.20f), 0.25f, 0.0f, urpLit);
            var matDinoLightGreen = GetOrCreateMaterial("M_Dino_LightGreen", new Color(0.48f, 0.62f, 0.32f), 0.25f, 0.0f, urpLit);
            var matDinoYellow = GetOrCreateMaterial("M_Dino_Yellow", new Color(0.82f, 0.72f, 0.35f), 0.25f, 0.0f, urpLit);
            var matDinoRed = GetOrCreateMaterial("M_Dino_Red", new Color(0.65f, 0.22f, 0.18f), 0.25f, 0.0f, urpLit);
            var matDinoDark = GetOrCreateMaterial("M_Dino_Dark", new Color(0.12f, 0.12f, 0.12f), 0.25f, 0.0f, urpLit);
            var matDinoBrown = GetOrCreateMaterial("M_Dino_Brown", new Color(0.45f, 0.32f, 0.22f), 0.25f, 0.0f, urpLit);

            // Hierarchy Categories per Scene Hierarchy Styling Rules
            GameObject catLighting = new GameObject("=== Lighting & Atmosphere ===");
            GameObject catGround = new GameObject("=== Ground & Terrain ===");
            GameObject catEnclosure = new GameObject("=== Electric Fence Enclosure ===");
            GameObject catGate = new GameObject("=== Security Gate & Entrance ===");
            GameObject catDinosaurs = new GameObject("=== Dinosaurs (Enclosure) ===");
            GameObject catViewpoint = new GameObject("=== Observation Deck & Road ===");
            GameObject catVisitors = new GameObject("=== Visitors (Background Characters) ===");
            GameObject catFoliage = new GameObject("=== Environment & Vegetation ===");

            // 2. Lighting & Atmosphere
            GameObject sunObj = new GameObject("Sun Light (Directional)");
            sunObj.transform.SetParent(catLighting.transform);
            sunObj.transform.rotation = Quaternion.Euler(48f, -32f, 0f);
            Light sun = sunObj.AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.color = new Color(1.0f, 0.95f, 0.88f);
            sun.intensity = 1.3f;
            sun.shadows = LightShadows.Soft;

            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.65f, 0.75f, 0.9f);
            RenderSettings.ambientEquatorColor = new Color(0.55f, 0.62f, 0.55f);
            RenderSettings.ambientGroundColor = new Color(0.28f, 0.35f, 0.22f);

            // 3. Ground & Terrain (Lush stylized green grass, no test patterns)
            Material matGrass = GetOrCreateMaterial("M_Park_LushGrass", new Color(0.24f, 0.52f, 0.18f), 0.05f, 0.0f, urpLit);

            GameObject ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.name = "Park Ground (Grass)";
            ground.transform.SetParent(catGround.transform);
            ground.transform.position = Vector3.zero;
            ground.transform.localScale = new Vector3(25f, 1f, 25f); // 250m x 250m
            ground.GetComponent<Renderer>().sharedMaterial = matGrass;

            // 4. Electric Fence Enclosure (Paddock)
            // Dimensions: X: -35 to +35 (70m), Z: 0 to 65 (65m)
            float xMin = -35f, xMax = 35f, zMin = 0f, zMax = 65f;
            float postSpacing = 5.0f;
            float fenceHeight = 4.5f;

            // Build Perimeter Posts & Wires
            BuildFenceLine(catEnclosure.transform, new Vector3(xMin, 0, zMin), new Vector3(xMin, 0, zMax), postSpacing, fenceHeight, matConcrete, matSteel, matCable, matHazard);
            BuildFenceLine(catEnclosure.transform, new Vector3(xMin, 0, zMax), new Vector3(xMax, 0, zMax), postSpacing, fenceHeight, matConcrete, matSteel, matCable, matHazard);
            BuildFenceLine(catEnclosure.transform, new Vector3(xMax, 0, zMax), new Vector3(xMax, 0, zMin), postSpacing, fenceHeight, matConcrete, matSteel, matCable, matHazard);
            // Front line with 12m opening in center for grand entrance
            BuildFenceLine(catEnclosure.transform, new Vector3(xMin, 0, zMin), new Vector3(-6f, 0, zMin), postSpacing, fenceHeight, matConcrete, matSteel, matCable, matHazard);
            BuildFenceLine(catEnclosure.transform, new Vector3(6f, 0, zMin), new Vector3(xMax, 0, zMin), postSpacing, fenceHeight, matConcrete, matSteel, matCable, matHazard);

            // 5. Grand Security Gate
            BuildSecurityGate(catGate.transform, new Vector3(0, 0, zMin), 12f, 7.5f, matConcrete, matSteel, matHazard, matDanger);

            // 6. Dinosaurs Placement & Scaling (Natural proportions relative to humans)
            // T-Rex (Apex predator, ~5.2m tall, centered in the paddock)
            PlaceDinosaur("Trex.fbx", catDinosaurs.transform, new Vector3(0f, 0f, 24f), Quaternion.Euler(0, -165f, 0), 1.35f, matDinoGreen, matDinoLightGreen, matDinoYellow, matDinoDark, matDinoRed);

            // Apatosaurus (Sauropod, ~9.5m tall, comfortably fits inside enclosure)
            PlaceDinosaur("Apatosaurus.fbx", catDinosaurs.transform, new Vector3(10f, 0f, 42f), Quaternion.Euler(0, -115f, 0), 0.95f, matDinoBrown, matDinoYellow, matDinoDark, matDinoGreen, null);

            // Stegosaurus (Plated herbivore, ~3.2m tall)
            PlaceDinosaur("Stegosaurus.fbx", catDinosaurs.transform, new Vector3(-16f, 0f, 20f), Quaternion.Euler(0, 65f, 0), 1.25f, matDinoGreen, matDinoRed, matDinoYellow, matDinoDark, null);

            // Triceratops (Three-horned herbivore, ~2.8m tall)
            PlaceDinosaur("Triceratops.fbx", catDinosaurs.transform, new Vector3(16f, 0f, 18f), Quaternion.Euler(0, -50f, 0), 1.25f, matDinoBrown, matDinoYellow, matDinoDark, matDinoLightGreen, null);

            // Parasaurolophus (Duck-billed crested dinosaur, ~3.0m tall)
            PlaceDinosaur("Parasaurolophus.fbx", catDinosaurs.transform, new Vector3(-16f, 0f, 38f), Quaternion.Euler(0, 120f, 0), 1.20f, matDinoYellow, matDinoGreen, matDinoDark, matDinoRed, null);

            // Velociraptor Pack (Agile predators, ~1.7m tall)
            PlaceDinosaur("Velociraptor.fbx", catDinosaurs.transform, new Vector3(-5f, 0f, 10f), Quaternion.Euler(0, -145f, 0), 0.95f, matDinoRed, matDinoYellow, matDinoDark, matDinoBrown, null);
            PlaceDinosaur("Velociraptor.fbx", catDinosaurs.transform, new Vector3(-8f, 0f, 11.5f), Quaternion.Euler(0, -130f, 0), 0.90f, matDinoGreen, matDinoYellow, matDinoDark, matDinoBrown, null);

            // 7. Elevated Observation Deck / Viewpoint
            // Situated just outside the fence from Z = -13 to -5, elevated 4.5m above ground
            Vector3 deckCenter = new Vector3(0f, 4.5f, -9f);
            BuildObservationDeck(catViewpoint.transform, deckCenter, 20f, 8f, matWood, matSteel, matConcrete);

            // 8. Visitor Road & Approach Path
            BuildVisitorRoad(catViewpoint.transform, new Vector3(0, 0.05f, -9f), matRoad);

            // 9. Background Characters (Visitors)
            // Visitors along the deck railing in direct camera view
            PlaceVisitor("Female_LookingUp.fbx", "Female_Hairstyle_1.fbx", catVisitors.transform, new Vector3(-1.3f, 4.5f, -5.7f), Quaternion.Euler(0, 15f, 0));
            PlaceVisitor("Male_LookingUp.fbx", "Male_Hairstyle_2.fbx", catVisitors.transform, new Vector3(1.3f, 4.5f, -5.7f), Quaternion.Euler(0, -15f, 0));
            PlaceVisitor("Woman_Standing_Waving.fbx", "Female_Hairstyle_2.fbx", catVisitors.transform, new Vector3(3.2f, 4.5f, -5.7f), Quaternion.Euler(0, -35f, 0));
            PlaceVisitor("Male_Standing_Hips.fbx", "Male_Hairstyle_1.fbx", catVisitors.transform, new Vector3(-3.2f, 4.5f, -5.7f), Quaternion.Euler(0, 35f, 0));
            PlaceVisitor("Female_Sitting_Cheering.fbx", "Female_Hairstyle_3.fbx", catVisitors.transform, new Vector3(-5.5f, 4.5f, -7.5f), Quaternion.Euler(0, 45f, 0));
            PlaceVisitor("Male_Walking.fbx", "Male_Hairstyle_3.fbx", catVisitors.transform, new Vector3(0.5f, 1.8f, -14.5f), Quaternion.Euler(0, 0f, 0)); // walking up stairs

            // 10. Environment Dressing (Trees, Rocks, Ferns, Bushes)
            PopulateVegetationAndRocks(catFoliage.transform, xMin, xMax, zMin, zMax);

            // 11. Camera Setup overlooking the park
            GameObject camObj = new GameObject("Main Camera");
            camObj.tag = "MainCamera";
            camObj.transform.SetParent(catViewpoint.transform);
            camObj.transform.position = new Vector3(0f, 6.1f, -7.2f); // behind & slightly above visitors
            camObj.transform.rotation = Quaternion.Euler(7.5f, 0f, 0f);
            Camera cam = camObj.AddComponent<Camera>();
            cam.fieldOfView = 65f;
            cam.nearClipPlane = 0.3f;
            cam.farClipPlane = 350f;
            camObj.AddComponent<AudioListener>();

            // Save Scene
            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene, ScenePath);
            AssetDatabase.SaveAssets();

            Debug.Log($"[DinosaurParkBuilder] Dinosaur Park Scene successfully built and saved to {ScenePath}!");
        }

        private static Material GetOrCreateMaterial(string name, Color color, float smoothness, float metallic, Shader shader)
        {
            string path = $"{ParkMaterialsPath}/{name}.mat";
            Material mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null)
            {
                mat = new Material(shader);
                mat.SetColor("_BaseColor", color);
                mat.SetFloat("_Smoothness", smoothness);
                mat.SetFloat("_Metallic", metallic);
                AssetDatabase.CreateAsset(mat, path);
            }
            return mat;
        }

        private static void BuildFenceLine(Transform parent, Vector3 start, Vector3 end, float spacing, float height, Material matBase, Material matPost, Material matWire, Material matSign)
        {
            Vector3 dir = (end - start).normalized;
            float totalDist = Vector3.Distance(start, end);
            int postCount = Mathf.Max(2, Mathf.RoundToInt(totalDist / spacing));

            // Low concrete foundation barrier
            GameObject baseWall = GameObject.CreatePrimitive(PrimitiveType.Cube);
            baseWall.name = "Fence Foundation Barrier";
            baseWall.transform.SetParent(parent);
            baseWall.transform.position = (start + end) * 0.5f + Vector3.up * 0.35f;
            baseWall.transform.rotation = Quaternion.LookRotation(dir);
            baseWall.transform.localScale = new Vector3(0.5f, 0.7f, totalDist);
            baseWall.GetComponent<Renderer>().sharedMaterial = matBase;

            // Vertical Posts
            for (int i = 0; i <= postCount; i++)
            {
                float t = (float)i / postCount;
                Vector3 postPos = Vector3.Lerp(start, end, t);

                GameObject post = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                post.name = $"Electric Fence Post ({i})";
                post.transform.SetParent(parent);
                post.transform.position = postPos + Vector3.up * (height * 0.5f);
                post.transform.localScale = new Vector3(0.35f, height * 0.5f, 0.35f);
                post.GetComponent<Renderer>().sharedMaterial = matPost;

                // High voltage hazard band
                if (i % 2 == 0)
                {
                    GameObject band = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                    band.name = "Hazard Warning Band";
                    band.transform.SetParent(post.transform);
                    band.transform.localPosition = new Vector3(0, 0.6f, 0);
                    band.transform.localScale = new Vector3(1.15f, 0.1f, 1.15f);
                    band.GetComponent<Renderer>().sharedMaterial = matSign;
                }
            }

            // Horizontal Electric High-Voltage Cables (5 rows)
            int cableCount = 5;
            float startY = 1.0f;
            float endY = height - 0.3f;
            for (int c = 0; c < cableCount; c++)
            {
                float wireY = Mathf.Lerp(startY, endY, (float)c / (cableCount - 1));
                GameObject wire = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                wire.name = $"Electric Cable (Row {c + 1})";
                wire.transform.SetParent(parent);
                wire.transform.position = (start + end) * 0.5f + Vector3.up * wireY;
                wire.transform.rotation = Quaternion.LookRotation(dir) * Quaternion.Euler(90, 0, 0);
                wire.transform.localScale = new Vector3(0.06f, totalDist * 0.5f, 0.06f);
                wire.GetComponent<Renderer>().sharedMaterial = matWire;
            }
        }

        private static void BuildSecurityGate(Transform parent, Vector3 center, float width, float height, Material matBase, Material matSteel, Material matHazard, Material matDanger)
        {
            GameObject gateGroup = new GameObject("Gate Entrance Structure");
            gateGroup.transform.SetParent(parent);
            gateGroup.transform.position = center;

            // Left & Right Gate Pillars
            float halfW = width * 0.5f;
            Vector3[] pillarPositions = new Vector3[] { new Vector3(-halfW, 0, 0), new Vector3(halfW, 0, 0) };

            foreach (var pos in pillarPositions)
            {
                GameObject pillar = GameObject.CreatePrimitive(PrimitiveType.Cube);
                pillar.name = "Security Gate Heavy Pillar";
                pillar.transform.SetParent(gateGroup.transform);
                pillar.transform.localPosition = pos + Vector3.up * (height * 0.5f);
                pillar.transform.localScale = new Vector3(1.8f, height, 1.8f);
                pillar.GetComponent<Renderer>().sharedMaterial = matBase;

                // Warning Beacon Light
                GameObject beacon = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                beacon.name = "Warning Beacon Lamp";
                beacon.transform.SetParent(pillar.transform);
                beacon.transform.localPosition = new Vector3(0, 0.55f, 0);
                beacon.transform.localScale = new Vector3(0.4f, 0.15f, 0.4f);
                beacon.GetComponent<Renderer>().sharedMaterial = matDanger;
            }

            // Overhead Gate Arch Header
            GameObject arch = GameObject.CreatePrimitive(PrimitiveType.Cube);
            arch.name = "Overhead Gate Security Beam";
            arch.transform.SetParent(gateGroup.transform);
            arch.transform.localPosition = new Vector3(0, height - 0.4f, 0);
            arch.transform.localScale = new Vector3(width + 1.8f, 0.9f, 1.2f);
            arch.GetComponent<Renderer>().sharedMaterial = matSteel;

            // Hazard Caution Sign on Arch
            GameObject sign = GameObject.CreatePrimitive(PrimitiveType.Cube);
            sign.name = "Caution High Voltage Signboard";
            sign.transform.SetParent(arch.transform);
            sign.transform.localPosition = new Vector3(0, 0, -0.6f);
            sign.transform.localScale = new Vector3(0.6f, 0.7f, 0.05f);
            sign.GetComponent<Renderer>().sharedMaterial = matHazard;

            // Steel Security Gates (Swung open like Jurassic Park)
            GameObject leftGate = GameObject.CreatePrimitive(PrimitiveType.Cube);
            leftGate.name = "Steel Gate Leaf (Left - Open)";
            leftGate.transform.SetParent(gateGroup.transform);
            leftGate.transform.localPosition = new Vector3(-halfW * 0.85f, (height - 1.2f) * 0.5f, 2.2f);
            leftGate.transform.localRotation = Quaternion.Euler(0, -65f, 0);
            leftGate.transform.localScale = new Vector3(halfW * 0.95f, height - 1.2f, 0.18f);
            leftGate.GetComponent<Renderer>().sharedMaterial = matSteel;

            GameObject rightGate = GameObject.CreatePrimitive(PrimitiveType.Cube);
            rightGate.name = "Steel Gate Leaf (Right - Open)";
            rightGate.transform.SetParent(gateGroup.transform);
            rightGate.transform.localPosition = new Vector3(halfW * 0.85f, (height - 1.2f) * 0.5f, 2.2f);
            rightGate.transform.localRotation = Quaternion.Euler(0, 65f, 0);
            rightGate.transform.localScale = new Vector3(halfW * 0.95f, height - 1.2f, 0.18f);
            rightGate.GetComponent<Renderer>().sharedMaterial = matSteel;
        }

        private static void BuildObservationDeck(Transform parent, Vector3 center, float width, float depth, Material matWood, Material matSteel, Material matBase)
        {
            GameObject deckRoot = new GameObject("Elevated Observation Platform");
            deckRoot.transform.SetParent(parent);
            deckRoot.transform.position = center;

            // Platform Deck Floor
            GameObject floor = GameObject.CreatePrimitive(PrimitiveType.Cube);
            floor.name = "Observation Deck Floor";
            floor.transform.SetParent(deckRoot.transform);
            floor.transform.localPosition = Vector3.zero;
            floor.transform.localScale = new Vector3(width, 0.35f, depth);
            floor.GetComponent<Renderer>().sharedMaterial = matWood;

            // Heavy Support Columns Underneath (no center obstruction)
            float hw = (width * 0.5f) - 1.0f;
            float hd = (depth * 0.5f) - 1.0f;
            Vector3[] colOffsets = new Vector3[]
            {
                new Vector3(-hw, 0, -hd), new Vector3(hw, 0, -hd),
                new Vector3(-hw, 0, hd), new Vector3(hw, 0, hd),
                new Vector3(-hw * 0.5f, 0, -hd), new Vector3(hw * 0.5f, 0, -hd)
            };

            foreach (var off in colOffsets)
            {
                GameObject col = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                col.name = "Deck Heavy Support Pillar";
                col.transform.SetParent(deckRoot.transform);
                col.transform.localPosition = new Vector3(off.x, -center.y * 0.5f, off.z);
                col.transform.localScale = new Vector3(0.7f, center.y * 0.5f, 0.7f);
                col.GetComponent<Renderer>().sharedMaterial = matBase;
            }

            // Safety Perimeter Railings (Slim modern safety handrail, non-obstructing)
            BuildDeckRailings(deckRoot.transform, width, depth, matSteel);

            // Roof Canopy / High Open Pavilion
            GameObject roof = GameObject.CreatePrimitive(PrimitiveType.Cube);
            roof.name = "Viewing Shelter Canopy";
            roof.transform.SetParent(deckRoot.transform);
            roof.transform.localPosition = new Vector3(0, 4.6f, 0);
            roof.transform.localScale = new Vector3(width + 1.5f, 0.25f, depth + 1.5f);
            roof.GetComponent<Renderer>().sharedMaterial = matWood;

            // Roof Support Posts (Only at rear & side corners, front line completely open)
            Vector3[] roofPostOffsets = new Vector3[]
            {
                new Vector3(-hw, 0, -hd), new Vector3(hw, 0, -hd),
                new Vector3(-hw, 0, hd * 0.7f), new Vector3(hw, 0, hd * 0.7f)
            };

            foreach (var off in roofPostOffsets)
            {
                GameObject post = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                post.name = "Canopy Timber Post";
                post.transform.SetParent(deckRoot.transform);
                post.transform.localPosition = new Vector3(off.x, 2.3f, off.z);
                post.transform.localScale = new Vector3(0.25f, 2.3f, 0.25f);
                post.GetComponent<Renderer>().sharedMaterial = matSteel;
            }

            // Access Staircase ramp from ground
            GameObject stairs = GameObject.CreatePrimitive(PrimitiveType.Cube);
            stairs.name = "Visitor Deck Stairs Ramp";
            stairs.transform.SetParent(deckRoot.transform);
            stairs.transform.localPosition = new Vector3(0, -center.y * 0.5f, -depth * 0.5f - 4f);
            stairs.transform.localRotation = Quaternion.Euler(22f, 0, 0);
            stairs.transform.localScale = new Vector3(3.5f, 0.3f, 9.5f);
            stairs.GetComponent<Renderer>().sharedMaterial = matWood;
        }

        private static void BuildDeckRailings(Transform parent, float width, float depth, Material matSteel)
        {
            float hw = width * 0.5f;
            float hd = depth * 0.5f;
            float rHeight = 1.15f;

            // Front Railing (Slim top handrail + slim bottom bar + baluster posts)
            GameObject topBar = GameObject.CreatePrimitive(PrimitiveType.Cube);
            topBar.name = "Front Railing Handrail";
            topBar.transform.SetParent(parent);
            topBar.transform.localPosition = new Vector3(0, rHeight, hd);
            topBar.transform.localScale = new Vector3(width, 0.08f, 0.12f);
            topBar.GetComponent<Renderer>().sharedMaterial = matSteel;

            GameObject bottomBar = GameObject.CreatePrimitive(PrimitiveType.Cube);
            bottomBar.name = "Front Railing Bottom Bar";
            bottomBar.transform.SetParent(parent);
            bottomBar.transform.localPosition = new Vector3(0, 0.12f, hd);
            bottomBar.transform.localScale = new Vector3(width, 0.06f, 0.08f);
            bottomBar.GetComponent<Renderer>().sharedMaterial = matSteel;

            // Vertical Balusters spaced along front
            int balusterCount = Mathf.RoundToInt(width / 1.8f);
            for (int b = 0; b <= balusterCount; b++)
            {
                float bx = Mathf.Lerp(-hw, hw, (float)b / balusterCount);
                GameObject post = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                post.name = $"Front Baluster ({b})";
                post.transform.SetParent(parent);
                post.transform.localPosition = new Vector3(bx, rHeight * 0.5f, hd);
                post.transform.localScale = new Vector3(0.06f, rHeight * 0.5f, 0.06f);
                post.GetComponent<Renderer>().sharedMaterial = matSteel;
            }

            // Left Railing (Slim)
            GameObject leftBar = GameObject.CreatePrimitive(PrimitiveType.Cube);
            leftBar.name = "Left Railing Handrail";
            leftBar.transform.SetParent(parent);
            leftBar.transform.localPosition = new Vector3(-hw, rHeight, 0);
            leftBar.transform.localScale = new Vector3(0.12f, 0.08f, depth);
            leftBar.GetComponent<Renderer>().sharedMaterial = matSteel;

            // Right Railing (Slim)
            GameObject rightBar = GameObject.CreatePrimitive(PrimitiveType.Cube);
            rightBar.name = "Right Railing Handrail";
            rightBar.transform.SetParent(parent);
            rightBar.transform.localPosition = new Vector3(hw, rHeight, 0);
            rightBar.transform.localScale = new Vector3(0.12f, 0.08f, depth);
            rightBar.GetComponent<Renderer>().sharedMaterial = matSteel;
        }

        private static void BuildVisitorRoad(Transform parent, Vector3 start, Material matRoad)
        {
            // Paved walkway from entrance road to deck
            GameObject road = GameObject.CreatePrimitive(PrimitiveType.Cube);
            road.name = "Visitor Main Road (Paved)";
            road.transform.SetParent(parent);
            road.transform.position = new Vector3(0, 0.04f, -32f);
            road.transform.localScale = new Vector3(6.0f, 0.08f, 40f);
            road.GetComponent<Renderer>().sharedMaterial = matRoad;

            // Pathway slabs from environment models
            string slabPrefab = $"{EnvModelsPath}/RockPath_Square_Wide.fbx";
            GameObject slabAsset = AssetDatabase.LoadAssetAtPath<GameObject>(slabPrefab);
            if (slabAsset != null)
            {
                for (float z = -45f; z <= -14f; z += 3.5f)
                {
                    GameObject slab = PrefabUtility.InstantiatePrefab(slabAsset) as GameObject;
                    slab.transform.SetParent(parent);
                    slab.transform.position = new Vector3(0, 0.07f, z);
                    slab.transform.localScale = new Vector3(1.8f, 1f, 1.8f);
                }
            }
        }

        private static void PlaceDinosaur(string fbxName, Transform parent, Vector3 pos, Quaternion rot, float scale, params Material[] customMats)
        {
            string fbxPath = $"{DinoBasePath}/{fbxName}";
            GameObject fbxAsset = AssetDatabase.LoadAssetAtPath<GameObject>(fbxPath);
            if (fbxAsset == null)
            {
                Debug.LogWarning($"[DinosaurParkBuilder] Dinosaur model not found at {fbxPath}");
                return;
            }

            GameObject dino = PrefabUtility.InstantiatePrefab(fbxAsset) as GameObject;
            dino.name = Path.GetFileNameWithoutExtension(fbxName);
            dino.transform.SetParent(parent);
            dino.transform.position = pos;
            dino.transform.rotation = rot;
            dino.transform.localScale = Vector3.one * scale;

            // Apply vibrant materials if renderer has slots
            var rend = dino.GetComponentInChildren<SkinnedMeshRenderer>();
            if (rend != null && customMats != null && customMats.Length > 0)
            {
                Material[] newMats = new Material[rend.sharedMaterials.Length];
                for (int m = 0; m < newMats.Length; m++)
                {
                    newMats[m] = customMats[m % customMats.Length];
                }
                rend.sharedMaterials = newMats;
            }
        }

        private static void PlaceVisitor(string fbxName, string hairName, Transform parent, Vector3 pos, Quaternion rot)
        {
            string charFolder = fbxName.StartsWith("Female") || fbxName.StartsWith("Woman") ? "Female" : "Male";
            string fbxPath = $"{CharBasePath}/{charFolder}/Poses/{fbxName}";
            GameObject charAsset = AssetDatabase.LoadAssetAtPath<GameObject>(fbxPath);
            if (charAsset == null) return;

            GameObject visitor = PrefabUtility.InstantiatePrefab(charAsset) as GameObject;
            visitor.name = Path.GetFileNameWithoutExtension(fbxName);
            visitor.transform.SetParent(parent);
            visitor.transform.position = pos;
            visitor.transform.rotation = rot;
            visitor.transform.localScale = Vector3.one * 1.0f; // 1:1 human scale

            // Attach matching hairstyle if available
            if (!string.IsNullOrEmpty(hairName))
            {
                string hairPath = $"{CharBasePath}/{charFolder}/Hairstyles/{hairName}";
                GameObject hairAsset = AssetDatabase.LoadAssetAtPath<GameObject>(hairPath);
                if (hairAsset != null)
                {
                    GameObject hair = PrefabUtility.InstantiatePrefab(hairAsset) as GameObject;
                    hair.transform.SetParent(visitor.transform);
                    hair.transform.localPosition = Vector3.zero;
                    hair.transform.localRotation = Quaternion.identity;
                    hair.transform.localScale = Vector3.one;
                }
            }
        }

        private static void PopulateVegetationAndRocks(Transform parent, float xMin, float xMax, float zMin, float zMax)
        {
            // Trees around outer paddock perimeter
            string[] treeModels = new string[]
            {
                "TwistedTree_1.fbx", "TwistedTree_3.fbx", "CommonTree_1.fbx", "CommonTree_2.fbx", "Pine_1.fbx", "Pine_3.fbx"
            };

            // Outer Perimeter Forest (dense border)
            for (float x = xMin - 8f; x <= xMax + 8f; x += 6.5f)
            {
                SpawnEnvProp(treeModels[Random.Range(0, treeModels.Length)], parent, new Vector3(x, 0, zMax + 5f), Random.Range(1.3f, 2.0f));
            }
            for (float z = zMin; z <= zMax; z += 7f)
            {
                SpawnEnvProp(treeModels[Random.Range(0, treeModels.Length)], parent, new Vector3(xMin - 6f, 0, z), Random.Range(1.3f, 2.0f));
                SpawnEnvProp(treeModels[Random.Range(0, treeModels.Length)], parent, new Vector3(xMax + 6f, 0, z), Random.Range(1.3f, 2.0f));
            }

            // Paddock interior natural features
            string[] rockModels = new string[] { "Rock_Medium_1.fbx", "Rock_Medium_2.fbx", "Rock_Medium_3.fbx" };
            SpawnEnvProp(rockModels[0], parent, new Vector3(6f, 0, 16f), 2.2f);
            SpawnEnvProp(rockModels[1], parent, new Vector3(-8f, 0, 18f), 2.8f);
            SpawnEnvProp(rockModels[2], parent, new Vector3(14f, 0, 36f), 3.2f);
            SpawnEnvProp(rockModels[0], parent, new Vector3(-22f, 0, 32f), 2.5f);

            // Shrubbery & Ferns inside paddock
            string[] plants = new string[] { "Fern_1.fbx", "Bush_Common.fbx", "Bush_Common_Flowers.fbx", "Flower_3_Group.fbx" };
            for (int i = 0; i < 22; i++)
            {
                float rx = Random.Range(xMin + 4f, xMax - 4f);
                float rz = Random.Range(zMin + 6f, zMax - 6f);
                SpawnEnvProp(plants[Random.Range(0, plants.Length)], parent, new Vector3(rx, 0, rz), Random.Range(1.0f, 1.8f));
            }
        }

        private static void SpawnEnvProp(string fbxName, Transform parent, Vector3 pos, float scale)
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

            // Apply environment materials to all child renderers
            foreach (Renderer rend in prop.GetComponentsInChildren<Renderer>())
            {
                if (rend == null) continue;

                if (fbxName.Contains("TwistedTree"))
                {
                    Material bark = AssetDatabase.LoadAssetAtPath<Material>($"{EnvMaterialsPath}/M_Bark_TwistedTree.mat");
                    Material leaves = AssetDatabase.LoadAssetAtPath<Material>($"{EnvMaterialsPath}/M_Leaves_TwistedTree.mat");
                    if (bark != null && leaves != null)
                    {
                        if (rend.sharedMaterials.Length >= 2)
                            rend.sharedMaterials = new Material[] { bark, leaves };
                        else if (rend.name.ToLower().Contains("leaf") || rend.name.ToLower().Contains("leaves"))
                            rend.sharedMaterial = leaves;
                        else
                            rend.sharedMaterial = bark;
                    }
                }
                else if (fbxName.Contains("CommonTree"))
                {
                    Material bark = AssetDatabase.LoadAssetAtPath<Material>($"{EnvMaterialsPath}/M_Bark_NormalTree.mat");
                    Material leaves = AssetDatabase.LoadAssetAtPath<Material>($"{EnvMaterialsPath}/M_Leaves_NormalTree.mat");
                    if (bark != null && leaves != null)
                    {
                        if (rend.sharedMaterials.Length >= 2)
                            rend.sharedMaterials = new Material[] { bark, leaves };
                        else if (rend.name.ToLower().Contains("leaf") || rend.name.ToLower().Contains("leaves"))
                            rend.sharedMaterial = leaves;
                        else
                            rend.sharedMaterial = bark;
                    }
                }
                else if (fbxName.Contains("Pine"))
                {
                    Material bark = AssetDatabase.LoadAssetAtPath<Material>($"{EnvMaterialsPath}/M_Bark_NormalTree.mat");
                    Material leaves = AssetDatabase.LoadAssetAtPath<Material>($"{EnvMaterialsPath}/M_Pine.mat");
                    if (bark != null && leaves != null)
                    {
                        if (rend.sharedMaterials.Length >= 2)
                            rend.sharedMaterials = new Material[] { bark, leaves };
                        else if (rend.name.ToLower().Contains("leaf") || rend.name.ToLower().Contains("leaves") || rend.name.ToLower().Contains("pine"))
                            rend.sharedMaterial = leaves;
                        else
                            rend.sharedMaterial = bark;
                    }
                }
                else if (fbxName.Contains("Rock"))
                {
                    Material rock = AssetDatabase.LoadAssetAtPath<Material>($"{EnvMaterialsPath}/M_Rocks.mat");
                    if (rock != null) rend.sharedMaterial = rock;
                }
                else if (fbxName.Contains("Bush") || fbxName.Contains("Fern") || fbxName.Contains("Flower") || fbxName.Contains("Clover"))
                {
                    Material leaves = AssetDatabase.LoadAssetAtPath<Material>($"{EnvMaterialsPath}/M_Leaves.mat");
                    Material flowers = AssetDatabase.LoadAssetAtPath<Material>($"{EnvMaterialsPath}/M_Flowers.mat");
                    if (fbxName.Contains("Flower") && flowers != null)
                        rend.sharedMaterial = flowers;
                    else if (leaves != null)
                        rend.sharedMaterial = leaves;
                }
            }
        }
    }
}
