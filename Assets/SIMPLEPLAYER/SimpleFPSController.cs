using UnityEngine;

#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

/// <summary>
/// Controlador FPS simple para Unity 6.
/// Requisitos:
/// - Este script en el GameObject del jugador.
/// - CharacterController en el mismo GameObject.
/// - Opcional: una Camera hija. Si no existe, el script crea una automáticamente.
///
/// Incluye:
/// - Movimiento WASD.
/// - Cámara en primera persona.
/// - Salto.
/// - Coyote Time.
/// - Jump Buffer.
/// - Crosshair circular.
/// - Bloqueo del cursor.
/// </summary>
[RequireComponent(typeof(CharacterController))]
public class SimpleFPSController : MonoBehaviour
{
    [Header("Movimiento")]
    [SerializeField, Min(0f)] private float moveSpeed = 5f;
    [SerializeField, Min(0f)] private float jumpHeight = 1.4f;
    [SerializeField] private float gravity = -22f;

    [Header("Salto")]
    [Tooltip("Tiempo después de abandonar el suelo durante el cual todavía puedes saltar.")]
    [SerializeField, Min(0f)] private float coyoteTime = 0.15f;

    [Tooltip("Tiempo durante el cual se recuerda una pulsación de salto hecha justo antes de tocar el suelo.")]
    [SerializeField, Min(0f)] private float jumpBufferTime = 0.15f;

    [Header("Cámara")]
    [SerializeField] private Camera playerCamera;
    [SerializeField, Min(0.01f)] private float mouseSensitivity = 2f;
    [SerializeField, Range(1f, 89f)] private float maxLookAngle = 85f;

    [Tooltip("Distancia que baja la cámara desde el punto más alto del CharacterController.")]
    [SerializeField, Min(0f)] private float cameraTopPadding = 0.12f;

    [Tooltip("Si está activado, coloca automáticamente la cámara cerca del tope del CharacterController.")]
    [SerializeField] private bool autoPositionCamera = true;

    [Header("Crosshair")]
    [SerializeField] private bool showCrosshair = true;
    [SerializeField, Range(2f, 32f)] private float crosshairSize = 8f;
    [SerializeField] private Color crosshairColor = Color.white;

    [Header("Cursor")]
    [SerializeField] private bool lockCursorOnStart = true;

    private CharacterController controller;

    private float verticalVelocity;
    private float cameraPitch;

    private float coyoteCounter;
    private float jumpBufferCounter;

    private Texture2D crosshairTexture;

    private void Awake()
    {
        controller = GetComponent<CharacterController>();

        SetupCamera();
        CreateCrosshairTexture();
    }

    private void Start()
    {
        if (lockCursorOnStart)
            SetCursorLocked(true);
    }

    private void Update()
    {
        HandleCursorToggle();
        HandleLook();
        HandleJumpTimers();
        HandleMovement();
    }

    private void SetupCamera()
    {
        if (playerCamera == null)
            playerCamera = GetComponentInChildren<Camera>(true);

        if (playerCamera == null)
        {
            GameObject cameraObject = new GameObject("PlayerCamera");
            cameraObject.transform.SetParent(transform);
            cameraObject.transform.localRotation = Quaternion.identity;

            playerCamera = cameraObject.AddComponent<Camera>();
            cameraObject.AddComponent<AudioListener>();
        }

        if (autoPositionCamera)
            PositionCameraAtTop();
    }

    private void PositionCameraAtTop()
    {
        // El tope real del CharacterController teniendo en cuenta su center.
        float topY = controller.center.y + (controller.height * 0.5f);

        Vector3 localPosition = playerCamera.transform.localPosition;
        localPosition.x = controller.center.x;
        localPosition.y = topY - cameraTopPadding;
        localPosition.z = controller.center.z;

        playerCamera.transform.localPosition = localPosition;
    }

    private void HandleLook()
    {
        if (Cursor.lockState != CursorLockMode.Locked)
            return;

        Vector2 lookInput = ReadLookInput();

        float yaw = lookInput.x;
        float pitch = lookInput.y;

        transform.Rotate(Vector3.up * yaw);

        cameraPitch -= pitch;
        cameraPitch = Mathf.Clamp(cameraPitch, -maxLookAngle, maxLookAngle);

        playerCamera.transform.localRotation = Quaternion.Euler(cameraPitch, 0f, 0f);
    }

    private void HandleJumpTimers()
    {
        if (controller.isGrounded)
            coyoteCounter = coyoteTime;
        else
            coyoteCounter -= Time.deltaTime;

        if (JumpPressedThisFrame())
            jumpBufferCounter = jumpBufferTime;
        else
            jumpBufferCounter -= Time.deltaTime;
    }

    private void HandleMovement()
    {
        bool grounded = controller.isGrounded;

        // Mantiene al CharacterController pegado al suelo sin acumular caída.
        if (grounded && verticalVelocity < 0f)
            verticalVelocity = -2f;

        // Jump Buffer + Coyote Time.
        if (jumpBufferCounter > 0f && coyoteCounter > 0f)
        {
            verticalVelocity = Mathf.Sqrt(jumpHeight * -2f * gravity);

            jumpBufferCounter = 0f;
            coyoteCounter = 0f;
        }

        Vector2 moveInput = ReadMoveInput();

        Vector3 horizontalMove =
            (transform.right * moveInput.x) +
            (transform.forward * moveInput.y);

        // Evita moverse más rápido en diagonal.
        if (horizontalMove.sqrMagnitude > 1f)
            horizontalMove.Normalize();

        verticalVelocity += gravity * Time.deltaTime;

        Vector3 velocity = horizontalMove * moveSpeed;
        velocity.y = verticalVelocity;

        CollisionFlags flags = controller.Move(velocity * Time.deltaTime);

        // Si golpeamos un techo, anulamos la velocidad ascendente.
        if ((flags & CollisionFlags.Above) != 0 && verticalVelocity > 0f)
            verticalVelocity = 0f;
    }

    private Vector2 ReadMoveInput()
    {
#if ENABLE_INPUT_SYSTEM
        Vector2 move = Vector2.zero;

        if (Keyboard.current != null)
        {
            if (Keyboard.current.aKey.isPressed) move.x -= 1f;
            if (Keyboard.current.dKey.isPressed) move.x += 1f;
            if (Keyboard.current.sKey.isPressed) move.y -= 1f;
            if (Keyboard.current.wKey.isPressed) move.y += 1f;
        }

        return Vector2.ClampMagnitude(move, 1f);
#else
        return Vector2.ClampMagnitude(
            new Vector2(Input.GetAxisRaw("Horizontal"), Input.GetAxisRaw("Vertical")),
            1f
        );
#endif
    }

    private Vector2 ReadLookInput()
    {
#if ENABLE_INPUT_SYSTEM
        if (Mouse.current == null)
            return Vector2.zero;

        // Mouse.delta son píxeles por frame. El factor 0.02 deja
        // mouseSensitivity en un rango cómodo parecido al Input clásico.
        return Mouse.current.delta.ReadValue() * (mouseSensitivity * 0.02f);
#else
        return new Vector2(
            Input.GetAxis("Mouse X") * mouseSensitivity,
            Input.GetAxis("Mouse Y") * mouseSensitivity
        );
#endif
    }

    private bool JumpPressedThisFrame()
    {
#if ENABLE_INPUT_SYSTEM
        return Keyboard.current != null && Keyboard.current.spaceKey.wasPressedThisFrame;
#else
        return Input.GetButtonDown("Jump");
#endif
    }

    private void HandleCursorToggle()
    {
        // ESC libera el cursor. Click izquierdo lo vuelve a capturar.
#if ENABLE_INPUT_SYSTEM
        if (Keyboard.current != null && Keyboard.current.escapeKey.wasPressedThisFrame)
            SetCursorLocked(false);

        if (Mouse.current != null &&
            Mouse.current.leftButton.wasPressedThisFrame &&
            Cursor.lockState != CursorLockMode.Locked)
        {
            SetCursorLocked(true);
        }
#else
        if (Input.GetKeyDown(KeyCode.Escape))
            SetCursorLocked(false);

        if (Input.GetMouseButtonDown(0) && Cursor.lockState != CursorLockMode.Locked)
            SetCursorLocked(true);
#endif
    }

    private void SetCursorLocked(bool locked)
    {
        Cursor.lockState = locked ? CursorLockMode.Locked : CursorLockMode.None;
        Cursor.visible = !locked;
    }

    private void CreateCrosshairTexture()
    {
        const int textureSize = 32;

        crosshairTexture = new Texture2D(
            textureSize,
            textureSize,
            TextureFormat.RGBA32,
            false
        );

        crosshairTexture.name = "Runtime_CircularCrosshair";
        crosshairTexture.filterMode = FilterMode.Bilinear;
        crosshairTexture.wrapMode = TextureWrapMode.Clamp;

        Vector2 center = new Vector2(
            (textureSize - 1) * 0.5f,
            (textureSize - 1) * 0.5f
        );

        float radius = textureSize * 0.38f;
        float softEdge = 1.5f;

        for (int y = 0; y < textureSize; y++)
        {
            for (int x = 0; x < textureSize; x++)
            {
                float distance = Vector2.Distance(new Vector2(x, y), center);

                float alpha = 1f - Mathf.InverseLerp(
                    radius - softEdge,
                    radius + softEdge,
                    distance
                );

                Color pixel = crosshairColor;
                pixel.a *= Mathf.Clamp01(alpha);

                crosshairTexture.SetPixel(x, y, pixel);
            }
        }

        crosshairTexture.Apply();
    }

    private void OnGUI()
    {
        if (!showCrosshair || crosshairTexture == null)
            return;

        float size = crosshairSize;

        Rect rect = new Rect(
            (Screen.width - size) * 0.5f,
            (Screen.height - size) * 0.5f,
            size,
            size
        );

        GUI.color = Color.white;
        GUI.DrawTexture(rect, crosshairTexture, ScaleMode.StretchToFill, true);
    }

    private void OnDestroy()
    {
        if (crosshairTexture != null)
            Destroy(crosshairTexture);
    }

#if UNITY_EDITOR
    private void OnValidate()
    {
        if (gravity > -0.01f)
            gravity = -0.01f;

        if (!Application.isPlaying)
            return;

        if (controller == null)
            controller = GetComponent<CharacterController>();

        if (autoPositionCamera && controller != null && playerCamera != null)
            PositionCameraAtTop();
    }
#endif
}
