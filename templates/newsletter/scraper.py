import twint

kwlist = ("moa", "donald", "duck")

for keyword in kwlist:
	# Configure
	c = twint.Config()
	c.Search = keyword
	c.Limit = 5
	c.Store_csv = True
	c.Custom["tweet"] = ["id"]
	c.Custom["user"] = ["bio"]
	c.Custom["username"] = ["username"]
	c.Custom["url"] = ["url"]
	c.Custom["likes"] = ["likes"]
	# Run
	twint.run.Search(c)