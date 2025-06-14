import math
import ctypes
import pyglet

pyglet.options["shadow_window"] = False
pyglet.options["debug_gl"] = False

import pyglet.gl as gl

import shader
import camera

import block_type
import texture_manager


class Window(pyglet.window.Window):
	def __init__(self, **args):
		super().__init__(**args)

		# create blocks

		self.texture_manager = texture_manager.Texture_manager(16, 16, 256)

		self.cobblestone = block_type.Block_type(self.texture_manager, "cobblestone", {"all": "cobblestone"}) # create each one of our blocks with the texture manager and a list of textures per face
		self.grass = block_type.Block_type(self.texture_manager, "grass", {"top": "grasstopnew", "bottom": "dirtnew", "sides": "grasssidenew"})
		self.moss = block_type.Block_type(self.texture_manager, "moss", {"all": "moss"})
		self.dirt = block_type.Block_type(self.texture_manager, "dirt", {"all": "dirtnew"})
		self.missingblock = block_type.Block_type(self.texture_manager, "missingblock", {"all": "missing"})
		self.clay = block_type.Block_type(self.texture_manager, "clay", {"all": "clay"})
		self.stone = block_type.Block_type(self.texture_manager, "stone", {"all": "stone"})
		self.andesite = block_type.Block_type(self.texture_manager, "andesite", {"all": "andesite"})
		self.diorite = block_type.Block_type(self.texture_manager, "diorite", {"all": "diorite"})
		self.sand = block_type.Block_type(self.texture_manager, "sand", {"all": "sand"})
		self.planks = block_type.Block_type(self.texture_manager, "planks", {"all": "planks"})
		self.log = block_type.Block_type(self.texture_manager, "log", {"top": "log_top", "bottom": "log_top", "sides": "log"})
		self.gravel = block_type.Block_type(self.texture_manager, "gravel", {"all": "gravel"})
		self.mud = block_type.Block_type(self.texture_manager, "mud", {"all": "dirt"})
		self.bricks = block_type.Block_type(self.texture_manager, "bricks", {"all": "bricks"})
		self.ironblock = block_type.Block_type(self.texture_manager, "ironblock", {"all": "ironblock"})
		self.diamondblock = block_type.Block_type(self.texture_manager, "diamondblock", {"all": "diamondblock"})
		self.goldblock = block_type.Block_type(self.texture_manager, "goldblock", {"all": "goldenblock"})
		self.emeraldblock = block_type.Block_type(self.texture_manager, "emeraldblock", {"all": "emeraldblock"})
		self.lilanthblock = block_type.Block_type(self.texture_manager, "lilanthblock", {"all": "lilanthblock"})
		self.ironpillar = block_type.Block_type(self.texture_manager, "ironpillar", {"top": "ironblock", "bottom": "ironblock", "sides": "ironpillar"})
		self.diamondpillar = block_type.Block_type(self.texture_manager, "diamondpillar", {"top": "diamondblock", "bottom": "diamondblock", "sides": "diamondpillar"})
		self.emeraldpillar = block_type.Block_type(self.texture_manager, "emeraldpillar", {"top": "emeraldblock", "bottom": "emeraldblock", "sides": "emeraldpillar"})
		self.lilanthpillar = block_type.Block_type(self.texture_manager, "lilanthillar", {"top": "lilanthblock", "bottom": "lilanthblock", "sides": "lilanthpillar"})
		self.stonepillar = block_type.Block_type(self.texture_manager, "stonepillar", {"top": "stone", "bottom": "stone", "sides": "stonepillar"})
		self.bedrock = block_type.Block_type(self.texture_manager, "bedrock", {"all": "bedrock"})

		self.texture_manager.generate_mipmaps()

		# create vertex array object

		self.vao = gl.GLuint(0)
		gl.glGenVertexArrays(1, ctypes.byref(self.vao))
		gl.glBindVertexArray(self.vao)

		# create vertex position vbo

		self.vertex_position_vbo = gl.GLuint(0)
		gl.glGenBuffers(1, ctypes.byref(self.vertex_position_vbo))
		gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vertex_position_vbo)

		gl.glBufferData(
			gl.GL_ARRAY_BUFFER,
			ctypes.sizeof(gl.GLfloat * len(self.grass.vertex_positions)),
			(gl.GLfloat * len(self.grass.vertex_positions))(*self.grass.vertex_positions),
			gl.GL_STATIC_DRAW,
		)

		gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, 0)
		gl.glEnableVertexAttribArray(0)

		# create tex coord vbo

		self.tex_coord_vbo = gl.GLuint(0)
		gl.glGenBuffers(1, ctypes.byref(self.tex_coord_vbo))
		gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.tex_coord_vbo)

		gl.glBufferData(
			gl.GL_ARRAY_BUFFER,
			ctypes.sizeof(gl.GLfloat * len(self.grass.tex_coords)),
			(gl.GLfloat * len(self.grass.tex_coords))(*self.grass.tex_coords),
			gl.GL_STATIC_DRAW,
		)

		gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, 0)
		gl.glEnableVertexAttribArray(1)

		# create shading value vbo

		self.shading_value_vbo = gl.GLuint(0)
		gl.glGenBuffers(1, ctypes.byref(self.shading_value_vbo))
		gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.shading_value_vbo)

		gl.glBufferData(
			gl.GL_ARRAY_BUFFER,
			ctypes.sizeof(gl.GLfloat * len(self.grass.shading_values)),
			(gl.GLfloat * len(self.grass.shading_values))(*self.grass.shading_values),
			gl.GL_STATIC_DRAW,
		)

		gl.glVertexAttribPointer(2, 1, gl.GL_FLOAT, gl.GL_FALSE, 0, 0)
		gl.glEnableVertexAttribArray(2)

		# create index buffer object

		self.ibo = gl.GLuint(0)
		gl.glGenBuffers(1, self.ibo)
		gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.ibo)

		gl.glBufferData(
			gl.GL_ELEMENT_ARRAY_BUFFER,
			ctypes.sizeof(gl.GLuint * len(self.grass.indices)),
			(gl.GLuint * len(self.grass.indices))(*self.grass.indices),
			gl.GL_STATIC_DRAW,
		)

		# create shader

		self.shader = shader.Shader("vert.glsl", "frag.glsl")
		self.shader_sampler_location = self.shader.find_uniform(b"texture_array_sampler")
		self.shader.use()

		# pyglet stuff

		pyglet.clock.schedule_interval(self.update, 1.0 / 100000)
		self.mouse_captured = False

		# camera stuff

		self.camera = camera.Camera(self.shader, self.width, self.height)

	def update(self, delta_time):
		print("FPS: {1.0 / delta_time}")
		
		
		if not self.mouse_captured:
			self.camera.input = [0, 0, 0]

		self.camera.update_camera(delta_time)

	def on_draw(self):
		self.camera.update_matrices()

		# bind textures

		gl.glActiveTexture(gl.GL_TEXTURE0)
		gl.glBindTexture(gl.GL_TEXTURE_2D_ARRAY, self.texture_manager.texture_array)
		gl.glUniform1i(self.shader_sampler_location, 0)

		# draw stuff

		gl.glEnable(gl.GL_DEPTH_TEST)
		gl.glClearColor(0.0, 0.0, 0.0, 1.0)
		self.clear()

		gl.glDrawElements(gl.GL_TRIANGLES, len(self.grass.indices), gl.GL_UNSIGNED_INT, None)

	# input functions

	def on_resize(self, width, height):
		print(f"Resize {width} * {height}")
		gl.glViewport(0, 0, width, height)

		self.camera.width = width
		self.camera.height = height

	def on_mouse_press(self, x, y, button, modifiers):
		self.mouse_captured = not self.mouse_captured
		self.set_exclusive_mouse(self.mouse_captured)

	def on_mouse_motion(self, x, y, delta_x, delta_y):
		if self.mouse_captured:
			sensitivity = 0.004

			self.camera.rotation[0] -= delta_x * sensitivity
			self.camera.rotation[1] += delta_y * sensitivity

			self.camera.rotation[1] = max(-math.tau / 4, min(math.tau / 4, self.camera.rotation[1]))

	def on_key_press(self, key, modifiers):
		if not self.mouse_captured:
			return

		if key == pyglet.window.key.D:
			self.camera.input[0] += 1
		elif key == pyglet.window.key.A:
			self.camera.input[0] -= 1
		elif key == pyglet.window.key.W:
			self.camera.input[2] += 1
		elif key == pyglet.window.key.S:
			self.camera.input[2] -= 1

		elif key == pyglet.window.key.SPACE:
			self.camera.input[1] += 1
		elif key == pyglet.window.key.LCTRL:
			self.camera.input[1] -= 1

	def on_key_release(self, key, modifiers):
		if not self.mouse_captured:
			return

		if key == pyglet.window.key.D:
			self.camera.input[0] -= 1
		elif key == pyglet.window.key.A:
			self.camera.input[0] += 1
		elif key == pyglet.window.key.W:
			self.camera.input[2] -= 1
		elif key == pyglet.window.key.S:
			self.camera.input[2] += 1

		elif key == pyglet.window.key.SPACE:
			self.camera.input[1] -= 1
		elif key == pyglet.window.key.LCTRL:
			self.camera.input[1] += 1


class Game:
	def __init__(self):
		self.config = gl.Config(double_buffer=True, major_version=3, minor_version=3, depth_size=16)
		self.window = Window(
			config=self.config, width=800, height=600, caption="Green Valley Treetops 0.1.0", resizable=True, vsync=False
		)

	def run(self):
		pyglet.app.run()


if __name__ == "__main__":
	game = Game()
	game.run()
