extends CharacterBody2D
class_name Player

signal throw_requested(origin: Vector2, direction: int)

const SPEED := 340.0
const JUMP_VELOCITY := -900.0
const THROW_COOLDOWN := 0.35
const GRAVITY := 2300.0

var facing := 1
var throw_timer := 0.0
var invuln_timer := 0.0
var lives := 3
var previous_jump_down := false
var previous_throw_down := false

@onready var sprite: Sprite2D = $Sprite2D
@onready var collision: CollisionShape2D = $CollisionShape2D


func set_visual(texture: Texture2D) -> void:
    var sprite_node := get_node_or_null("Sprite2D") as Sprite2D
    if sprite_node:
        sprite_node.texture = texture


func _physics_process(delta: float) -> void:
    throw_timer = max(0.0, throw_timer - delta)
    invuln_timer = max(0.0, invuln_timer - delta)

    var axis := _read_axis()
    velocity.x = axis * SPEED
    if absf(axis) > 0.05:
        facing = 1 if axis > 0 else -1
        sprite.flip_h = facing < 0

    var jump_down := _jump_down()
    if jump_down and not previous_jump_down and is_on_floor():
        velocity.y = JUMP_VELOCITY
    previous_jump_down = jump_down

    var throw_down := _throw_down()
    if throw_down and not previous_throw_down and throw_timer <= 0.0:
        throw_timer = THROW_COOLDOWN
        throw_requested.emit(global_position + Vector2(22 * facing, -10), facing)
    previous_throw_down = throw_down

    velocity.y += GRAVITY * delta
    move_and_slide()

    if invuln_timer > 0.0 and int(Time.get_ticks_msec() / 65.0) % 2 == 0:
        sprite.visible = false
    else:
        sprite.visible = true


func take_hit(push_direction: int) -> bool:
    if invuln_timer > 0.0:
        return false

    lives -= 1
    invuln_timer = 1.1
    velocity.x = 260.0 * push_direction
    velocity.y = -420.0
    return true


func hitbox() -> Rect2:
    var rectangle := collision.shape as RectangleShape2D
    var size := rectangle.size
    return Rect2(global_position - size * 0.5, size)


func _read_axis() -> float:
    var axis := 0.0
    if Input.is_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT):
        axis -= 1.0
    if Input.is_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT):
        axis += 1.0

    if Input.get_connected_joypads().size() > 0:
        var joy_axis := Input.get_joy_axis(0, JOY_AXIS_LEFT_X)
        if absf(joy_axis) > 0.2:
            axis = joy_axis

    return clampf(axis, -1.0, 1.0)


func _jump_down() -> bool:
    if Input.is_key_pressed(KEY_SPACE) or Input.is_key_pressed(KEY_W) or Input.is_key_pressed(KEY_UP):
        return true
    if Input.get_connected_joypads().size() > 0:
        return Input.is_joy_button_pressed(0, JOY_BUTTON_A)
    return false


func _throw_down() -> bool:
    if Input.is_key_pressed(KEY_J) or Input.is_key_pressed(KEY_C) or Input.is_key_pressed(KEY_ENTER):
        return true
    if Input.get_connected_joypads().size() > 0:
        return Input.is_joy_button_pressed(0, JOY_BUTTON_B) or Input.is_joy_button_pressed(0, JOY_BUTTON_X)
    return false
