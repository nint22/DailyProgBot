#!/usr/bin/python

# System imports
import datetime

# Reddit interface import
# Dev site is https://github.com/praw-dev/praw
import praw

# Google data API
# Wrapped through a third party dev: https://github.com/burnash/gspread
import gspread

# General password stored in a diff. file
# Global vars are all caps below
import AccountDetails

# Returns a string in the format of "1/17/2013", always rounding up to Mon, Wed, or Fri
def GetAssumedDate():
  
	# Current date
	Now = datetime.datetime.today()
	
	# Push over if needed
	if Now.weekday() == 1: # Tue. to Wed.
		Now += timedelta(days=1)
	elif Now.weekday() == 3: # Thu. to Fri.
		Now += timedelta(days=1)
	elif Now.weekday() == 6: # Sun. to Mon.
		Now += timedelta(days=1)
	
	# Done!
	return Now.strftime("%m/%d/%y")


# Utility string-search function: given a start and stop string, return the string within that character pair, starting at a specific string index
# Returns an empty string on failure
def GetSubstringSpecial(SourceString, StartingPos, StartChar, EndChar):
	
	# Seek first char
	StartIndex = SourceString.find(StartChar, StartingPos)
	if StartIndex < 0:
		return ""
	
	# Seek second char
	EndIndex = SourceString.find(EndChar, StartIndex)
	if EndIndex < 0:
		return ""
	
	# Substring out the target
	return SourceString[StartIndex + 1:EndIndex] # +1 because we want to ignore the start char

# Utility string-replacement function: given a start and stop string, set the string within that character pair, starting at a specific string index
# Returns the string once done, or the empty string on error
def SetSubstringSpecial(SourceString, TargetString, StartingPos, StartChar, EndChar):
	
	# Seek first char
	StartIndex = SourceString.find(StartChar, StartingPos)
	if StartIndex < 0:
		return ""
	
	# Seek second char
	EndIndex = SourceString.find(EndChar, StartIndex)
	if EndIndex < 0:
		return ""
	
	# Replace substring
	return SourceString[:StartIndex] + TargetString + SourceString[EndIndex:]


# Overall wrapper function - all you need is the difficulty you want to post
# Difficulty is an integer that maps to 0:easy, 1:intermediate, 2:hard
def PostChallenge(DifficultyIndex):
	
	# Save what the difficulty string is
	DifficultyString = ['Easy', 'Intermediate', 'Hard'][DifficultyIndex]
	
	### Part 1: Retrieve challenge
	
	# Login with your Google account
	gc = gspread.login(AccountDetails.GSPREAD_USERNAME, AccountDetails.GSPREAD_PASSWORD)
	
	# Open a worksheet from spreadsheet with one shot
	wks = gc.open("r/DailyProgrammer Challenge Submissions").sheet1
	
	# Set to a valid row index if target is found, else set to -1
	TargetRowIndex = -1
	
	# For each row, check if there exists any non-posted easy-level challenges..
	for RowIndex in range(2, wks.row_count):
		
		# Get the difficulty type and post-status
		DifficultyType = wks.acell('C%d' % RowIndex).value
		PostStatus = wks.acell('M%d' % RowIndex).value
		
		# If no data at all, then we're done parsing..
		if DifficultyType == None:
			break
		
		# If it is "easy" and there is no post status
		elif DifficultyType.lower() == DifficultyString.lower() and (PostStatus == None or len(PostStatus) <= 0):
			TargetRowIndex = RowIndex
			break
	
	# Error-check
	if TargetRowIndex < 0:
		print "Error: Unable to find any queued challenges that are '%s'" % DifficultyString
		return
	
	# Fill out the structure we will be posting!
	ChallengeTitle = wks.acell('B%d' % RowIndex).value
	ChallengeUserName = wks.acell('D%d' % RowIndex).value
	ChallengeDescription = wks.acell('E%d' % RowIndex).value
	ChallengeInputDescription = wks.acell('F%d' % RowIndex).value
	ChallengeOutputDescription = wks.acell('K%d' % RowIndex).value
	ChallengeInputSample = wks.acell('G%d' % RowIndex).value
	ChallengeOutputSample = wks.acell('L%d' % RowIndex).value
	ChallengeInput = wks.acell('I%d' % RowIndex).value
	ChallengeSolution  = wks.acell('J%d' % RowIndex).value
	ChallengeNote = wks.acell('H%d' % RowIndex).value
	
	### Part 2: Post to Reddit
	
	# Create reddit interface with username & password
	# Note: we don't care about oAuth2, since this isn't that important
	PrawInterface = praw.Reddit(user_agent='DailyProgrammerBot 1.0 by /u/nint22 github.com/nint22/DailyProgBot/')
	
	if DifficultyIndex == 0:
		PrawInterface.login(AccountDetails.EASY_USERNAME, AccountDetails.EASY_PASSWORD)
	elif DifficultyIndex == 1:
		PrawInterface.login(AccountDetails.INTER_USERNAME, AccountDetails.INTER_PASSWORD)
	elif DifficultyIndex == 2:
		PrawInterface.login(AccountDetails.HARD_USERNAME, AccountDetails.HARD_PASSWORD)
	
	# Update the side bar (i.e. update the top link)
	# First, we pull out the old side-bar text, then increment the challenge number, and finally insert the post's URL
	
	# 1. Find the settings string
	DPSettings = PrawInterface.get_settings('dailyprogrammer')
	
	# 2. Find the number (always between '#' and ':', but check for the appropriate line...)
	LineOffset = 0
	if DifficultyIndex == 0:
		LineOffset = DPSettings['description'].find('1.')
	elif DifficultyIndex == 1:
		LineOffset = DPSettings['description'].find('2.')
	elif DifficultyIndex == 2:
		LineOffset = DPSettings['description'].find('3.')
	
	# Find and increment
	ChallengeNumber = GetSubstringSpecial(DPSettings['description'], LineOffset, '#', ':')
	ChallengeNumber = int(ChallengeNumber)
	ChallengeNumber += 1
	
	# Generate the text format
	PostTitle = "[%s] Challenge #%d [%s] %s" % (GetAssumedDate(), ChallengeNumber, DifficultyString, ChallengeTitle)
	PostText = 	"""
# [](#%sIcon) *(%s)*: %s
%s
\n*Author: %s*
# Formal Inputs & Outputs
## Input Description
%s
## Output Description
%s
# Sample Inputs & Outputs
## Sample Input
%s
## Sample Output
%s
# Challenge Input
%s
## Challenge Input Solution
%s
# Note
%s
				""" % (DifficultyString, DifficultyString, ChallengeTitle, ChallengeDescription, ChallengeUserName, ChallengeInputDescription, ChallengeOutputDescription, ChallengeInputSample, ChallengeOutputSample, ChallengeInput, ChallengeSolution, ChallengeNote)
	
	# Submit a post and retain the URL
	SubmitResult = PrawInterface.submit('dailyprogrammer', PostTitle, text=PostText)
	PostURL = SubmitResult.url
	
	# 3. Update the side-bar
	if DifficultyIndex == 0:
		DPSettings['description'] = SetSubstringSpecial(DPSettings['description'], "1. [Monday\'s Challenge #%d: %s](%s)" % (ChallengeNumber, DifficultyString, PostURL), 0, '1.', '\n')
	elif DifficultyIndex == 1:
		DPSettings['description'] = SetSubstringSpecial(DPSettings['description'], "2. [Wednesday\'s Challenge #%d: %s](%s)" % (ChallengeNumber, DifficultyString, PostURL), 0, '2.', '\n')
	elif DifficultyIndex == 2:
		DPSettings['description'] = SetSubstringSpecial(DPSettings['description'], "3. [Friday\'s Challenge #%d: %s](%s)" % (ChallengeNumber, DifficultyString, PostURL), 0, '3.', '\n')
	else:
		print "Error: Unknown difficulty type"
		return
	
	# Commit these changes to reddit
	PrawInterface.get_subreddit('dailyprogrammer').update_settings(description=DPSettings['description'])
	
	# Let the table know we are using this data; this is done last to make sure the post was successful!
	wks.update_acell('M%d' % TargetRowIndex, 'true')


# Main application entry point
def main():
	
	# What day of the week are we? This decides the difficulty type!
	DayOfWeek = datetime.datetime.today().weekday()
	
	# Is Sun. night or Mon. morning; we post for monday
	if DayOfWeek == 6 or DayOfWeek == 0:
		PostChallenge(0)
	# Is Tue. night or Wed. morning; we post for wednesday
	elif DayOfWeek == 1 or DayOfWeek == 2:
		PostChallenge(1)
	# Is Thu. night or Fri. morning; we post for friday
	elif DayOfWeek == 3 or DayOfWeek == 4:
		PostChallenge(2)


# Standard main function
if __name__ == '__main__':
	main()
