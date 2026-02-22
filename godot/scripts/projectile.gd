extends Area2D
class_name Projectile

signal enemy_hit(enemy: Enemy)
signal player_hit(direction: int)

var velocity := Vector2.ZERO
var from_enemy := false
var lifetime := 3.0

@onready var sprite: Sprite2D = $Sprite2D


func _ready() -> void:
    body_entered.connect(_on_body_entered)


func setup(start_position: Vector2, direction: int, enemy_shot: bool, texture: Texture2D, tint: Color) -> void:
    global_position = start_position
    from_enemy = enemy_shot
    var sprite_node := get_node_or_null("Sprite2D") as Sprite2D
    if sprite_node:
        sprite_node.texture = texture
        sprite_node.modulate = tint

    if enemy_shot:
        velocity = Vector2(420.0 * direction, 0.0)
        collision_mask = 3
    else:
        velocity = Vector2(680.0 * direction, -110.0)
        collision_mask = 5


func _physics_process(delta: float) -> void:
    lifetime -= delta
    if lifetime <= 0.0:
        queue_free()
        return

    if not from_enemy:
        velocity.y += 900.0 * delta

    global_position += velocity * delta
    rotation += velocity.x * delta * 0.004

    if global_position.x < -180 or global_position.x > 6200 or global_position.y > 760 or global_position.y < -180:
        queue_free()


func _on_body_entered(body: Node) -> void:
    if from_enemy and body is Player:
        var direction := -1 if velocity.x > 0.0 else 1
        player_hit.emit(direction)
        queue_free()
        return

    if not from_enemy and body is Enemy:
        enemy_hit.emit(body)
        queue_free()
        return

    if body is StaticBody2D:
        queue_free()
