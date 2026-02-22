extends CharacterBody2D
class_name Enemy

signal shoot_requested(origin: Vector2, direction: int)

@export var kind := "waiter"
@export var patrol_min_x := 0.0
@export var patrol_max_x := 0.0
@export var patrol_speed := 95.0

const GRAVITY := 2300.0

var direction := 1
var player_x := 0.0
var shoot_timer := 0.0

@onready var sprite: Sprite2D = $Sprite2D
@onready var collision: CollisionShape2D = $CollisionShape2D


func _physics_process(delta: float) -> void:
    shoot_timer = max(0.0, shoot_timer - delta)

    var speed := patrol_speed
    var distance_to_player := player_x - global_position.x

    if kind == "waiter" and absf(distance_to_player) < 185.0:
        direction = 1 if distance_to_player > 0 else -1
        speed *= 1.7

    if kind == "police" and absf(distance_to_player) < 390.0 and shoot_timer <= 0.0:
        shoot_timer = 1.7
        var throw_direction := 1 if distance_to_player > 0 else -1
        shoot_requested.emit(global_position + Vector2(throw_direction * 15, -18), throw_direction)

    velocity.x = speed * direction
    velocity.y += GRAVITY * delta
    move_and_slide()

    if global_position.x < patrol_min_x:
        global_position.x = patrol_min_x
        direction = 1
    elif global_position.x > patrol_max_x:
        global_position.x = patrol_max_x
        direction = -1

    sprite.flip_h = direction < 0


func set_visual(texture: Texture2D) -> void:
    var sprite_node := get_node_or_null("Sprite2D") as Sprite2D
    if sprite_node:
        sprite_node.texture = texture


func hitbox() -> Rect2:
    var rectangle := collision.shape as RectangleShape2D
    var size := rectangle.size
    return Rect2(global_position - size * 0.5, size)
