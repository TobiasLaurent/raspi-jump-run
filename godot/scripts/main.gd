extends Node2D

const WORLD_WIDTH := 6000.0
const SCREEN_WIDTH := 960.0
const SCREEN_HEIGHT := 540.0
const GROUND_Y := 460.0
const GOAL_BEERS := 8

const PLAYER_SCENE := preload("res://scenes/player.tscn")
const ENEMY_SCENE := preload("res://scenes/enemy.tscn")
const COLLECTIBLE_SCENE := preload("res://scenes/collectible.tscn")
const PROJECTILE_SCENE := preload("res://scenes/projectile.tscn")

const PLAYER_TEXTURE := preload("res://assets/generated/player.png")
const WAITER_TEXTURE := preload("res://assets/generated/waiter.png")
const POLICE_TEXTURE := preload("res://assets/generated/police.png")
const BEER_TEXTURE := preload("res://assets/generated/beer.png")
const PRETZEL_TEXTURE := preload("res://assets/generated/pretzel.png")
const MUG_TEXTURE := preload("res://assets/generated/mug.png")

@onready var camera: Camera2D = $Camera2D
@onready var level: Node2D = $Level
@onready var entities: Node2D = $Entities
@onready var score_label: Label = $CanvasLayer/ScoreLabel
@onready var stats_label: Label = $CanvasLayer/StatsLabel
@onready var message_label: Label = $CanvasLayer/MessageLabel
@onready var overlay_panel: ColorRect = $CanvasLayer/OverlayPanel
@onready var overlay_title: Label = $CanvasLayer/OverlayPanel/OverlayTitle
@onready var overlay_subtitle: Label = $CanvasLayer/OverlayPanel/OverlaySubtitle
@onready var overlay_prompt: Label = $CanvasLayer/OverlayPanel/OverlayPrompt

var state := "running"
var score := 0
var beers := 0
var pretzels := 0
var message := ""
var message_timer := 0.0

var world_rects: Array[Rect2] = []
var enemies: Array[Enemy] = []
var player: Player


func _ready() -> void:
	randomize()
	camera.limit_left = 0
	camera.limit_right = int(WORLD_WIDTH)
	camera.limit_top = 0
	camera.limit_bottom = int(SCREEN_HEIGHT)
	new_game()


func _process(delta: float) -> void:
	message_timer = max(0.0, message_timer - delta)
	_update_hud()
	queue_redraw()


func _physics_process(delta: float) -> void:
	if state != "running":
		return

	for enemy in enemies:
		enemy.player_x = player.global_position.x

	for enemy in enemies:
		if enemy.hitbox().intersects(player.hitbox()):
			var push := -1 if player.global_position.x > enemy.global_position.x else 1
			player.take_hit(push)

	if player.global_position.y > 760.0:
		if player.take_hit(-1):
			player.global_position = Vector2(maxf(60.0, player.global_position.x - 100.0), 410.0)

	if player.lives <= 0:
		_show_overlay("Game Over", "Waiters and police ended your beer quest.", "Press SPACE / A to retry")
		state = "game_over"
		_set_simulation_enabled(false)
		return

	if player.global_position.x >= WORLD_WIDTH - 80.0:
		if beers >= GOAL_BEERS:
			_show_overlay(
				"Prost! You Won",
				"Score %d | Beer %d | Pretzels %d" % [score, beers, pretzels],
                "Press SPACE / A to play again"
			)
			state = "win"
			_set_simulation_enabled(false)
			return

		var missing := GOAL_BEERS - beers
		message = "Need %d more beer(s) to enter Oktoberfest." % missing
		message_timer = 2.0
		player.global_position.x = WORLD_WIDTH - 84.0

	var cam_target_x := clampf(player.global_position.x, SCREEN_WIDTH * 0.5, WORLD_WIDTH - SCREEN_WIDTH * 0.5)
	camera.global_position.x = lerpf(camera.global_position.x, cam_target_x, minf(1.0, delta * 8.0))
	camera.global_position.y = SCREEN_HEIGHT * 0.5


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_ESCAPE:
			get_tree().quit()
			return
		if event.keycode == KEY_F11:
			_toggle_fullscreen()
			return
		if state != "running" and event.keycode in [KEY_SPACE, KEY_ENTER]:
			new_game()
			return

	if event is InputEventJoypadButton and event.pressed:
		if state != "running" and event.button_index == JOY_BUTTON_A:
			new_game()


func new_game() -> void:
	score = 0
	beers = 0
	pretzels = 0
	message = "Collect beer and pretzels. Reach the festival gate."
	message_timer = 5.0
	state = "running"
	overlay_panel.visible = false

	enemies.clear()
	world_rects.clear()
	for child in level.get_children():
		child.queue_free()
	for child in entities.get_children():
		child.queue_free()

	_build_level()
	_spawn_player()
	_spawn_collectibles()
	_spawn_enemies()
	_set_simulation_enabled(true)

	camera.global_position = Vector2(SCREEN_WIDTH * 0.5, SCREEN_HEIGHT * 0.5)


func _build_level() -> void:
	_add_static_rect(Rect2(0.0, GROUND_Y, WORLD_WIDTH, SCREEN_HEIGHT - GROUND_Y))

	var platforms := [
		Rect2(320.0, 390.0, 170.0, 22.0),
		Rect2(760.0, 350.0, 220.0, 22.0),
		Rect2(1220.0, 402.0, 160.0, 22.0),
		Rect2(1580.0, 338.0, 190.0, 22.0),
		Rect2(2020.0, 372.0, 200.0, 22.0),
		Rect2(2480.0, 326.0, 180.0, 22.0),
		Rect2(2880.0, 402.0, 220.0, 22.0),
		Rect2(3380.0, 348.0, 190.0, 22.0),
		Rect2(3800.0, 382.0, 200.0, 22.0),
		Rect2(4280.0, 328.0, 210.0, 22.0),
		Rect2(4740.0, 368.0, 210.0, 22.0),
		Rect2(5230.0, 330.0, 180.0, 22.0),
	]
	for platform in platforms:
		_add_static_rect(platform)


func _add_static_rect(rect: Rect2) -> void:
	world_rects.append(rect)
	var body := StaticBody2D.new()
	body.collision_layer = 1
	body.collision_mask = 0
	body.global_position = rect.position + rect.size * 0.5

	var collision_shape := CollisionShape2D.new()
	var shape := RectangleShape2D.new()
	shape.size = rect.size
	collision_shape.shape = shape

	body.add_child(collision_shape)
	level.add_child(body)


func _spawn_player() -> void:
	player = PLAYER_SCENE.instantiate() as Player
	player.global_position = Vector2(90.0, 410.0)
	player.throw_requested.connect(_on_player_throw_requested)
	entities.add_child(player)
	player.set_visual(PLAYER_TEXTURE)


func _spawn_collectibles() -> void:
	for x in range(240, int(WORLD_WIDTH) - 200, 220):
		var kind := "beer" if randf() < 0.62 else "pretzel"
		var y := 420.0 if kind == "beer" else 424.0
		_spawn_collectible(kind, Vector2(float(x), y))

	for rect in world_rects:
		if rect.position.y >= GROUND_Y - 1.0:
			continue
		if randf() < 0.75:
			var kind := "beer" if randf() < 0.65 else "pretzel"
			var y := rect.position.y - 22.0
			_spawn_collectible(kind, Vector2(rect.get_center().x, y))


func _spawn_collectible(kind: String, position_world: Vector2) -> void:
	var item := COLLECTIBLE_SCENE.instantiate() as Collectible
	item.kind = kind
	item.value = 30 if kind == "beer" else 20
	item.global_position = position_world
	if kind == "beer":
		item.set_visual(BEER_TEXTURE)
	else:
		item.set_visual(PRETZEL_TEXTURE)
	item.collected.connect(_on_collectible_collected)
	entities.add_child(item)


func _spawn_enemies() -> void:
	var specs := [
		{"kind": "waiter", "x": 560.0, "min_x": 500.0, "max_x": 910.0, "speed": 95.0},
		{"kind": "police", "x": 1360.0, "min_x": 1260.0, "max_x": 1610.0, "speed": 86.0},
		{"kind": "waiter", "x": 2200.0, "min_x": 2100.0, "max_x": 2480.0, "speed": 100.0},
		{"kind": "police", "x": 3120.0, "min_x": 3000.0, "max_x": 3360.0, "speed": 92.0},
		{"kind": "waiter", "x": 4050.0, "min_x": 3940.0, "max_x": 4320.0, "speed": 104.0},
		{"kind": "police", "x": 4950.0, "min_x": 4800.0, "max_x": 5300.0, "speed": 100.0},
	]

	for spec in specs:
		var enemy := ENEMY_SCENE.instantiate() as Enemy
		enemy.kind = spec["kind"]
		enemy.global_position = Vector2(spec["x"], 410.0)
		enemy.patrol_min_x = spec["min_x"]
		enemy.patrol_max_x = spec["max_x"]
		enemy.patrol_speed = spec["speed"]
		if enemy.kind == "waiter":
			enemy.set_visual(WAITER_TEXTURE)
		else:
			enemy.set_visual(POLICE_TEXTURE)
			enemy.shoot_requested.connect(_on_enemy_shoot_requested)
		entities.add_child(enemy)
		enemies.append(enemy)


func _on_collectible_collected(kind: String, value: int) -> void:
	score += value
	if kind == "beer":
		beers += 1
	else:
		pretzels += 1


func _on_player_throw_requested(origin: Vector2, direction: int) -> void:
	var shot := PROJECTILE_SCENE.instantiate() as Projectile
	shot.setup(origin, direction, false, MUG_TEXTURE, Color.WHITE)
	shot.enemy_hit.connect(_on_projectile_enemy_hit)
	shot.player_hit.connect(_on_projectile_player_hit)
	entities.add_child(shot)


func _on_enemy_shoot_requested(origin: Vector2, direction: int) -> void:
	var shot := PROJECTILE_SCENE.instantiate() as Projectile
	shot.setup(origin, direction, true, MUG_TEXTURE, Color(0.6, 0.8, 1.0, 1.0))
	shot.enemy_hit.connect(_on_projectile_enemy_hit)
	shot.player_hit.connect(_on_projectile_player_hit)
	entities.add_child(shot)


func _on_projectile_enemy_hit(enemy: Enemy) -> void:
	if not is_instance_valid(enemy):
		return
	score += 60
	enemies.erase(enemy)
	enemy.queue_free()


func _on_projectile_player_hit(direction: int) -> void:
	player.take_hit(direction)


func _set_simulation_enabled(enabled: bool) -> void:
	if is_instance_valid(player):
		player.set_physics_process(enabled)
	for enemy in enemies:
		if is_instance_valid(enemy):
			enemy.set_physics_process(enabled)
	for child in entities.get_children():
		if child is Projectile:
			child.set_physics_process(enabled)


func _show_overlay(title: String, subtitle: String, prompt: String) -> void:
	overlay_panel.visible = true
	overlay_title.text = title
	overlay_subtitle.text = subtitle
	overlay_prompt.text = prompt


func _toggle_fullscreen() -> void:
	var mode := DisplayServer.window_get_mode()
	if mode == DisplayServer.WINDOW_MODE_FULLSCREEN:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
	else:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)


func _update_hud() -> void:
	var lives := player.lives if is_instance_valid(player) else 0
	score_label.text = "Score %d" % score
	stats_label.text = "Beer %d/%d  Pretzels %d  Lives %d" % [beers, GOAL_BEERS, pretzels, lives]
	if message_timer > 0.0:
		message_label.text = message
	else:
		message_label.text = ""


func _draw() -> void:
	var cam_x: float = camera.global_position.x

	draw_rect(Rect2(cam_x - 1200.0, -500.0, 3000.0, 700.0), Color(0.49, 0.78, 0.95), true)
	draw_rect(Rect2(cam_x - 1200.0, 140.0, 3000.0, 300.0), Color(0.56, 0.82, 0.98), true)

	for i in range(-2, 12):
		var mountain_x: float = float(i) * 280.0 + floorf(cam_x * 0.15)
		var points := PackedVector2Array([
			Vector2(mountain_x, 300.0),
			Vector2(mountain_x + 120.0, 175.0),
			Vector2(mountain_x + 240.0, 300.0),
		])
		draw_colored_polygon(points, Color(0.46, 0.57, 0.72))

	draw_rect(Rect2(0.0, GROUND_Y, WORLD_WIDTH, SCREEN_HEIGHT - GROUND_Y), Color(0.25, 0.64, 0.38), true)
	draw_rect(Rect2(0.0, GROUND_Y, WORLD_WIDTH, 8.0), Color(0.18, 0.45, 0.27), true)

	for rect in world_rects:
		if rect.position.y >= GROUND_Y - 1.0:
			continue
		draw_rect(rect, Color(0.63, 0.45, 0.27), true)
		draw_rect(Rect2(rect.position.x, rect.position.y + rect.size.y - 5.0, rect.size.x, 5.0), Color(0.48, 0.34, 0.2), true)

	var gate := Rect2(WORLD_WIDTH - 65.0, GROUND_Y - 128.0, 55.0, 128.0)
	draw_rect(gate, Color(0.44, 0.28, 0.16), true)
	draw_rect(Rect2(gate.position.x + 4.0, gate.position.y + 6.0, gate.size.x - 8.0, gate.size.y - 10.0), Color(0.62, 0.44, 0.27), true)
