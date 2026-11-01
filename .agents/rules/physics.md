# Unity Physics Architecture & Best Practices Rule

When writing, refactoring, or diagnosing Unity game physics (both PhysX/MonoBehaviour and Unity Physics / DOTS):

## 1. Golden Rules of Game Physics Architecture

1. **Never Move Static Colliders at Runtime**:
   - Moving static colliders causes an expensive rebuild of the static Bounding Volume Hierarchy (BVH) and triggers physics engine performance spikes.
   - For moving platforms, elevators, doors, or animated environment objects, always make them **Kinematic Rigid Bodies**.

2. **Move Kinematics via Velocity, Not Transform Position**:
   - Setting a kinematic body's transform directly is treated as instant teleportation; resting dynamic bodies will not inherit momentum and will clip or tunnel.
   - Always set `velocity.Linear` (or `Rigidbody.MovePosition` in PhysX) so the solver factors the velocity into contact constraints and pushes resting objects smoothly.

3. **Never Overwrite Dynamic Velocity with Direct Hard Assignments**:
   - Direct velocity overwrites wipe out solver collision response, momentum, and restitution, leading to wall penetration and clipping.
   - Use `ApplyLinearImpulse` or `ApplyExplosionForce` (or `Rigidbody.AddForce` in PhysX) to accumulate movement force on top of physical simulation.

4. **Collider Performance Hierarchy**:
   - **Primitives (Sphere, Box, Capsule, Cylinder)**: $\mathcal{O}(1)$ or minimal cost. Always prefer primitives.
   - **Compound Colliders**: Superior to concave meshes. Combine primitives for complex bodies or character hitboxes.
   - **Mesh Colliders**: Extremely expensive. Never use mesh colliders on dynamic bodies; only use convex or convex hull on dynamic objects, and use concave mesh colliders strictly on static environment props.
   - **Avoid Giant AABBs**: Break expansive floors or walls into modular pieces so broadphase bounding boxes don't span the entire map.

5. **Entity System Ordering (Unity Physics / DOTS)**:
   - **Forbidden in Simulation**: Never add/remove components, create, or destroy entities between `PhysicsInitializeGroup` and `ExportPhysicsWorld`. Always use an `EntityCommandBuffer` played back in `AfterPhysicsSystemGroup`.
   - **Forbidden Writes**: Never write to `PhysicsVelocity` or `LocalTransform` between `PhysicsInitializeGroup` and `ExportPhysicsWorld` (writes will be clobbered).
   - **Gameplay Updates**: Place custom physics interaction systems in `[UpdateInGroup(typeof(AfterPhysicsSystemGroup))]`.

6. **Filter Collisions and Queries**:
   - When firing raycasts, sweeps, or overlap queries (`CastRay`, `CastCollider`), always assign a valid `CollisionFilter` (`Filter = CollisionFilter.Default` or layer mask). A default-initialized unassigned filter mask will hit 0 objects.
   - Check `details.EstimatedImpulse > threshold` in collision events to discard continuous resting contacts.

7. **Breakable Constraints**:
   - In Unity Physics (DOTS), exceeding a joint's break threshold does not automatically sever the joint; it raises an `ImpulseEvent`. Code must consume `sim.ImpulseEvents` and destroy the joint entity.
