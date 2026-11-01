using System.Collections.Generic;
using UnityEngine;

namespace MiniGame
{
    /// <summary>
    /// Spawns and manages atmospheric birds soaring and circling above the dinosaur park.
    /// Provides dynamic sky life with natural flocking, banking, and wing flapping.
    /// </summary>
    public class AmbientBirdSystem : MonoBehaviour
    {
        [Header("Flock Settings")]
        [SerializeField] private int birdCount = 12;
        [SerializeField] private Vector3 skyCenter = new Vector3(0f, 28f, 25f);
        [SerializeField] private float flightRadius = 45f;
        [SerializeField] private float minHeight = 20f;
        [SerializeField] private float maxHeight = 38f;
        [SerializeField] private float flightSpeed = 9.5f;

        private List<BirdAgent> birds = new List<BirdAgent>();

        private class BirdAgent
        {
            public GameObject go;
            public Transform leftWing;
            public Transform rightWing;
            public float orbitAngle;
            public float orbitRadius;
            public float orbitSpeed;
            public float height;
            public float heightFrequency;
            public float flapFrequency;
            public float flapPhase;
            public float basePitch;
        }

        private void Start()
        {
            Material birdMat = new Material(Shader.Find("Universal Render Pipeline/Lit"));
            birdMat.color = new Color(0.2f, 0.22f, 0.24f); // dark avian plumage silhouette
            birdMat.SetFloat("_Smoothness", 0.3f);

            for (int i = 0; i < birdCount; i++)
            {
                var bird = CreateBirdGameObject($"Park_Bird_{i}", birdMat);
                bird.go.transform.SetParent(transform);

                bird.orbitAngle = Random.Range(0f, Mathf.PI * 2f);
                bird.orbitRadius = flightRadius * Random.Range(0.6f, 1.25f);
                bird.orbitSpeed = (flightSpeed / bird.orbitRadius) * (Random.value > 0.15f ? 1f : -0.7f);
                bird.height = Random.Range(minHeight, maxHeight);
                bird.heightFrequency = Random.Range(0.3f, 0.7f);
                bird.flapFrequency = Random.Range(4f, 7f);
                bird.flapPhase = Random.Range(0f, Mathf.PI * 2f);
                bird.basePitch = Random.Range(-4f, 6f);

                birds.Add(bird);
            }
        }

        private void Update()
        {
            float dt = Time.deltaTime;
            float t = Time.time;

            foreach (var bird in birds)
            {
                bird.orbitAngle += bird.orbitSpeed * dt;

                // Circular/elliptical soaring trajectory with gentle thermal wobble
                float x = skyCenter.x + Mathf.Cos(bird.orbitAngle) * bird.orbitRadius;
                float z = skyCenter.z + Mathf.Sin(bird.orbitAngle) * (bird.orbitRadius * 0.85f);
                float y = bird.height + Mathf.Sin(t * bird.heightFrequency + bird.flapPhase) * 3.5f;

                Vector3 targetPos = new Vector3(x, y, z);
                Vector3 prevPos = bird.go.transform.position;
                Vector3 velocity = (targetPos - prevPos);

                bird.go.transform.position = targetPos;

                if (velocity.sqrMagnitude > 0.0001f)
                {
                    Quaternion targetRot = Quaternion.LookRotation(velocity.normalized, Vector3.up);
                    // Add natural banking into turns
                    float bankAngle = -bird.orbitSpeed * 35f;
                    targetRot *= Quaternion.Euler(bird.basePitch, 0f, bankAngle);
                    bird.go.transform.rotation = Quaternion.Slerp(bird.go.transform.rotation, targetRot, dt * 6f);
                }

                // Animate wing flapping
                float flap = Mathf.Sin(t * bird.flapFrequency + bird.flapPhase);
                float wingAngle = flap * 28f;

                if (bird.leftWing != null)
                    bird.leftWing.localRotation = Quaternion.Euler(0f, 0f, wingAngle);
                if (bird.rightWing != null)
                    bird.rightWing.localRotation = Quaternion.Euler(0f, 0f, -wingAngle);
            }
        }

        private BirdAgent CreateBirdGameObject(string name, Material mat)
        {
            GameObject birdObj = new GameObject(name);

            // Fuselage / Bird Body
            GameObject body = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            body.name = "Body";
            body.transform.SetParent(birdObj.transform);
            body.transform.localPosition = Vector3.zero;
            body.transform.localRotation = Quaternion.Euler(90f, 0f, 0f);
            body.transform.localScale = new Vector3(0.22f, 0.65f, 0.22f);
            body.GetComponent<Renderer>().sharedMaterial = mat;
            Destroy(body.GetComponent<Collider>());

            // Tail
            GameObject tail = GameObject.CreatePrimitive(PrimitiveType.Cube);
            tail.name = "Tail";
            tail.transform.SetParent(birdObj.transform);
            tail.transform.localPosition = new Vector3(0f, 0.05f, -0.6f);
            tail.transform.localScale = new Vector3(0.35f, 0.04f, 0.45f);
            tail.GetComponent<Renderer>().sharedMaterial = mat;
            Destroy(tail.GetComponent<Collider>());

            // Left Wing Pivot & Mesh
            GameObject leftPivot = new GameObject("LeftWingPivot");
            leftPivot.transform.SetParent(birdObj.transform);
            leftPivot.transform.localPosition = new Vector3(-0.15f, 0.05f, 0.1f);

            GameObject leftWing = GameObject.CreatePrimitive(PrimitiveType.Cube);
            leftWing.name = "LeftWingMesh";
            leftWing.transform.SetParent(leftPivot.transform);
            leftWing.transform.localPosition = new Vector3(-0.55f, 0f, 0f);
            leftWing.transform.localRotation = Quaternion.Euler(0f, -12f, 0f);
            leftWing.transform.localScale = new Vector3(1.1f, 0.035f, 0.4f);
            leftWing.GetComponent<Renderer>().sharedMaterial = mat;
            Destroy(leftWing.GetComponent<Collider>());

            // Right Wing Pivot & Mesh
            GameObject rightPivot = new GameObject("RightWingPivot");
            rightPivot.transform.SetParent(birdObj.transform);
            rightPivot.transform.localPosition = new Vector3(0.15f, 0.05f, 0.1f);

            GameObject rightWing = GameObject.CreatePrimitive(PrimitiveType.Cube);
            rightWing.name = "RightWingMesh";
            rightWing.transform.SetParent(rightPivot.transform);
            rightWing.transform.localPosition = new Vector3(0.55f, 0f, 0f);
            rightWing.transform.localRotation = Quaternion.Euler(0f, 12f, 0f);
            rightWing.transform.localScale = new Vector3(1.1f, 0.035f, 0.4f);
            rightWing.GetComponent<Renderer>().sharedMaterial = mat;
            Destroy(rightWing.GetComponent<Collider>());

            // Overall bird scale
            birdObj.transform.localScale = Vector3.one * 1.15f;

            return new BirdAgent
            {
                go = birdObj,
                leftWing = leftPivot.transform,
                rightWing = rightPivot.transform
            };
        }
    }
}
