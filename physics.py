import math
from math3d import vec3
from objects import *
from forces import *

class Universe():
	def __init__(self, timestep=0.001):
		self.forces = []
		self.particles = []
		self.springs = []
		self.time = 0
		self.steps = 0
		self.timestep = timestep
		self.k, self.v = 0, 0
		self.objects = {}
		self.max_id = 0
		self.resolution = - int(math.log10(timestep))
	
	def addForce(self, f):
		self.forces += [f]

	def add(self, x):
		if isinstance(x, Particle):
			self.particles += [x]
			x.universe = self
		elif isinstance(x, Spring):
			self.springs += [x]
			x.universe = self
		self.max_id += 1
		self.objects[self.max_id] = x
		return self.max_id

	def getForce(self, p):
		F = vec3(0,0,0)
		for force in self.forces:
			F += force.getForce(p)
		return F

	def step(self):
		"Forward Euler Step Forward"
		# for each particle calculate total force acting on it
		dt = self.timestep
		for p in self.particles:
			F = self.getForce(p)
			acc = F/p.mass
			p._new_pos = p.pos + dt * p.vel
			p._new_vel = p.vel + dt * acc
		# for double buffering
		for p in self.particles:
			p.update()
		self.time += dt
		self.steps += 1

	def run(self, time = 1):
		while abs(self.time - time) > 1e-7:
			self.step()
		
	def data(self):
		pdata = [p.data() for p in self.particles]
		sdata = [s.data() for s in self.springs]
		return {'t': round(self.time, self.resolution), 'particles': pdata, 'springs': sdata}
	
	def updateEnergy(self):
		self.k,self.v = 0,0
		gravity = [x for x in self.forces if isinstance(x, GravityForce)]
		if len(gravity) == 0:
			gravity = None
		else:
			gravity = gravity[0]
		for p in self.particles:
			if isinstance(p, FixedParticle):
				continue
			self.k += (p.mass * p.vel.length() ** 2) / 2
			if gravity is not None:
				self.v += (- p.mass * gravity.g * p.pos)
		for s in self.springs:
			extension = (s.p1.pos - s.p2.pos).length() - s.l
			self.v += (s.k * extension ** 2) / 2
	
	def infolog(self):
		self.updateEnergy()
		print("<t, K, V, E>:\t%.3f\t\t%f\t%f\t%f" % (self.time, self.k, self.v, self.k+self.v))
