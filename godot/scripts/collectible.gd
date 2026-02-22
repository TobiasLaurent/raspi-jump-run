extends Area2D
class_name Collectible

signal collected(kind: String, value: int)

@export var kind := "beer"
@export var value := 30

var base_y := 0.0
var bob_time := 0.0

@onready var sprite: Sprite2D = $Sprite2D


func _ready() -> void:
	base_y = global_position.y
	bob_time = randf() * TAU
	body_entered.connect(_on_body_entered)


func _process(delta: float) -> void:
	bob_time += delta * 3.4
	global_position.y = base_y + sin(bob_time) * 4.0


func set_visual(texture: Texture2D) -> void:
	var sprite_node := get_node_or_null("Sprite2D") as Sprite2D
	if sprite_node:
		sprite_node.texture = texture


func _on_body_entered(body: Node) -> void:
	if body is Player:
		collected.emit(kind, value)
		queue_free()
