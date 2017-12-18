class Statline:
	def __init__(self, stats):
		self.pass_yds = stats[0]
		self.pass_tds = stats[1]
		self.interceptions = stats[2]
		self.rush_yds = stats[3]
		self.rush_tds = stats[4]
		self.fumbles = stats[5]
		self.rec_yds = stats[6]
		self.rec_tds = stats[7]
		self.k_made = stats[8]
		self.k_missed = stats[9]
		self.xp_made = stats[10]
		self.xp_missed = stats[11]
		self.pa = stats[12]
		self.sacks = stats[13]
		self.safeties = stats[14]
		self.ints_for = stats[15]
		self.fum_rec = stats[16]


class Player:
	def __init__(self, f_name, l_name, team, position, stats):
		self.f_name = f_name
		self.l_name = l_name
		self.team = team
		self.position = position
		self.stats = Statline(stats)
