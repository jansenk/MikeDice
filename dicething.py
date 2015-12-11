import random, sys, string
#Hi everyone! I am currently in the market for a dice roll calculator/manipulator.
#Basically, it would have the following functionality 
#     (all dice are the same size [currently d6, though having the ability to modify that would be cool]):
#-Add a single die of a specified color to the pool
#-Subtract a single die of a specified color from the pool
#
#-Roll the dice all at once
#
# Bonuses and Penalties after rolling (activates if you have the bonus or penalty checked) (can be acquired multiple times):
#-Bonus: Flip a single die if it's a 1 to a 6, 3 to a 4, or a 2 to a 5 automatically
#-Bonus: Add 1 to a single die of a specified color to bring it to 5 automatically
#-Penalty: Subtract 1 from a single die of a specified color if <= 5 automatically
#-Penalty: Subtract the highest single die from the pool automatically.
#It should output the final data either in a spreadsheet or graphical format. Having icons next to "what was modified with bonuses and penalties" would be useful as well.
#Adding in a "target number of successes in a given color" would be nice too,
#  as would having the ability to fuse dice of one value together of a different color to make one of another color.

# Modifier Stuff
class Modifier:
	def act(self, dice):
		selectedDie = self.select(dice)
		if selectedDie is None:
			#print self.__class__.__name__ + " got no dice"
			return None
		#print self.__class__.__name__ + " got " + str(selectedDie)
		self.modify(selectedDie)
		return selectedDie
	def select(self, dice):
		#print "searching"
		#print self.sideSelectionOrder
		for targetSide in self.sideSelectionOrder:
			#print targetSide
			for die in dice:
				#print str(die)
				if die.up == targetSide:
					#print "returning  " + str(die)
					return die
		return None
	def modify(self, die):
		raise NotImplementedException()
	def __str__(self):
		return self.__class__.__name__

#Flips 1-6, 2-5, 3-4
class FlipBonus(Modifier):
	flips = {1:6, 3:4, 2:5}
	def __init__(self):
		self.sideSelectionOrder = (1, 2, 3)
		self.priority = 0
	def modify(self, die):
		die.modifiers.append(self)
		die.up = FlipBonus.flips[die.up]

# Adds 1 to a die
class AddOneBonus(Modifier):
	def __init__(self):
		self.sideSelectionOrder = (4, 3, 2, 1)
		self.priority = 1
	def modify(self, die):
		die.modifiers.append(self)
		die.up += 1

# Subs one from a die
class SubOnePenalty(Modifier):
	def __init__(self):
		self.sideSelectionOrder = (6, 5)
		self.priority = 2
	def modify(self, die):
		die.modifiers.append(self)
		die.up -= 1

# Removed the highest Dice
class HighestNegatedPenalty(Modifier):
	def __init__(self):
		self.sideSelectionOrder = (6, 5)
		self.priority = 3
	def modify(self, die):
		die.modifiers.append(self)
		die.up = 0

# ----------- Pool -------------
class Pool:
	def __init__(self):
		self.dice = {color:[] for color in Color.list()}
		self.modifiers = []
	def addDie(self, color, sides=6):
		self.dice[color].append(Die(color, sides))
	def diceAsList(self):
		return [item for sublist in self.dice.values() for item in sublist] if len(self.dice) > 0 else []
	def addModifier(self, modifierIndex):
		if modifierIndex == 0:
			self.modifiers.append(FlipBonus())
		elif modifierIndex == 1:
			self.modifiers.append(AddOneBonus())
		elif modifierIndex == 2:
			self.modifiers.append(SubOnePenalty())
		else:
			self.modifiers.append(HighestNegatedPenalty())
	def roll(self, applyModifiers=True, report=True):
		for die in self.diceAsList():
			die.roll()
		#print "premod"
		#self.report()

		if applyModifiers:
			self.applyModifiers()

		if report:
			#print "postreport"
			self.report()

	def applyModifiers(self):
		self.modifiers.sort(key=lambda m: m.priority)
		for modifier in self.modifiers:
			modifier.act(self.diceAsList())
	def report(self):
		print "---------------------"
		print "--------ROLL---------"
		print "-------RESULTS-------"
		print "---------------------"
		if len(self.dice) == 0:
			print "Pool is empty"
		for color, dice in self.dice.iteritems():
			if not len(dice) == 0:
				print "%s pool: " % color 
				total = 0
				for die in dice:
					print str(die)
					total += die.up
				print "total: %d" % total


	def __str__(self):
		diceString = ""
		for die in self.diceAsList():
			diceString += str(die) + " "
		modString = ""
		for mod in self.modifiers:
			modString += str(mod) + " "
		return "Dice: [ %s]\nModifiers: [%s]" % (diceString, modString)


# ----------- Die ---------------
class Die:
	def __init__(self, color, sides=6):
		self.sides = sides
		self.color = color
		self.up = 1
		self.original = 1
		self.modifiers = []
	def roll(self):
		self.original = random.randint(1, self.sides)
		self.up = self.original
		self.modifiers = []
		return self.up
	def __str__(self):
		modifierString = ""
		if len(self.modifiers) == 0:
			modifierString = "no modifiers" 
		else:
			for modifier in self.modifiers:
				modifierString += " " + str(modifier)

		return "(%d (%d) of %d, %s, %s)" % (self.up,
								   self.original, 
								   self.sides, 
								   self.color, 
								   modifierString)


# ----------- Color ----------------
class Color:
	Red = 'red'
	Orange = 'orange'
	Yellow = 'yellow'
	Green = 'green'
	Blue = 'blue'
	Purple = 'purple'
	White = 'white'
	Black = 'black'
	@staticmethod
	def list():
		return [Color.Red, Color.Orange, Color.Yellow, Color.Green, Color.Blue, Color.Purple, Color.White, Color.Black]
	@staticmethod
	def parse(parseString):
		if parseString in Color.list():
			return parseString
		lower = string.lower(parseString)
		if lower in Color.list():
			return lower
		return None


def main():
	pool = Pool()
	while True:
		print str(pool)
		choice = raw_input("1) (A)dd die \n2) (D)elete die \n3) Add (M)odifier \n4) D(e)lete Modifier \n5)(R)oll Dice\n>> ")
		choice = choice[0]
		if choice in ["1", "a", "A"]:
			colorInput = raw_input("Color: (question mark for list):")
			parsedColor = Color.parse(colorInput)
			if colorInput == "?":
				print Color.list()
			elif not colorInput:
				print "invalid color"
				continue
			else:
				pool.addDie(parsedColor)
		elif choice in ["2", "D", "d"]:
			dl = pool.diceAsList()
			for i, die in enumerate(dl):
				print "%d) %s" % (i, die)
			selection = int(raw_input(">> "))
			if selection < 0 or selection > len(dl):
				print "invalid index"
				continue
			else:
				selectionDie = dl[selection]
				pool.dice[selectionDie.color].remove(selectionDie)
		elif choice in ["3", "M", "m"]:
			print "1) Flip 2) Add1 3) Sub1 4) DropHigh"
			selection = int(raw_input(">> "))
			pool.addModifier(selection-1)
		elif choice in ["4", "E", "e"]:
			for i, mod in enumerate(pool.modifiers):
				print "%d) %s" % (i, mod)
			selection = int(raw_input(">> "))
			if selection < 0 or selection > len(pool.modifiers):
				print "invalid index"
				continue
			else:
				pool.modifiers.pop(selection -1)
		elif choice in ["5", "R", "r"]:
			pool.roll()
		print "----------------------------------------"

if __name__ == "__main__":
	main()
