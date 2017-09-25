import time
import praw
import datetime
import operator
import obot

def median(lst):
    quotient, remainder = divmod(len(lst), 2)
    if remainder:
        return sorted(lst)[quotient]
    return sum(sorted(lst)[quotient - 1:quotient + 1]) / 2.

subreddit = input("What subreddit to run for? >>> ")
days  = int(input("How many days to check for? >>> "))

print("Starting process, hang on tight")
bot = praw.Reddit(user_agent='/r/{} post analysis'.format(subreddit),
                  client_id=obot.clientId,
                  client_secret=obot.clientSecret,
                  username=obot.name,
                  password=obot.passw)
print("Connection made")

statV = {}
statA = {}
stat  = {}
statM = {}
statS = {}
links = []

print("Fetching posts. This may take a while")
posts = list(bot.subreddit(subreddit).new(limit=1000))
postamount = len(posts)
print("Posts fetched! {} got".format(postamount))
amount = 0
for y, i in enumerate(posts):
    if i.is_self:
        self = "SELFPOST"
    else:
        if "i.redd.it" in i.url:
            self = "IMAGE"
        elif "imgur.com" in i.url:
            self = "IMAGE"
        else:
            self = "LINK"
            links.append(i.url)
    createdfrm = datetime.datetime.utcfromtimestamp(int(i.created_utc))
    nowtime = time.time()
    nowfrm = datetime.datetime.utcfromtimestamp(int(nowtime))
    diff = nowfrm - createdfrm
    if diff.total_seconds() < 24*3600:
        print("Post is not older than 24 hours, skipping")
        continue
    if diff.total_seconds() > 86400 * days:
        print("Post is older than {} days, ending task".format(days))
        break
    amount += 1
    flair = i.link_flair_css_class
    if flair == "Worldbuild?":
        flair = "Conlang"
    upvotes = i.score
    statV[flair] = statV.get(flair, 0) + upvotes
    statA[flair] = statA.get(flair, 0) + 1
    statV[self] = statV.get(self, 0) + upvotes
    statA[self] = statA.get(self, 0) + 1
    statM[flair] = statM.get(flair, []) + [upvotes]
    statM[self] = statM.get(self, []) + [upvotes]
    print("{}/{}: {} - {} ({}) - {} upvotes".format(y, postamount, i.title, flair, self, upvotes))

    last = diff.total_seconds() / 86400

for key, value in statV.items():
    stat[key] = round(statV[key] / statA[key])

for key, value in statM.items():
    statS[key] = round(median(value))

print(links)
print("\n+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=\n")
print("Ran through {} posts of {}, ({} being the goal) with the last one being {} days old".format(amount, subreddit, len(posts), last))
print("Average upvotes of the past {} days, categorized by flair type:".format(days))
longest = 0
for i in stat:
    if len(str(i)) > longest:
        longest = len(i)

longest += 1

for key, value in sorted(stat.items(), key=operator.itemgetter(1)):
    print("{}{}({}){} : {} average upvotes".format(key, " " * (longest - len(str(key))), statA[key], " " * (3 - len(str(statA[key]))), value))

print("")
print("Median upvotes of the past {} days, categorized by flair type:".format(days))
for key, value in sorted(statS.items(), key=operator.itemgetter(1)):
    print("{}{}({}){} : {} upvotes".format(key, " " * (longest - len(str(key))), statA[key], " " * (3- len(str(statA[key]))), value))