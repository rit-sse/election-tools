# SSE Election Tools

This repository contains various scripts and guides that help run the SSE
Primary Officer Election.

## How to Run an Election

As of this writing, RIT's survey system is Qualtrics. You can find it located
at http://rit.edu/survey. Students can use this site to create their own
surveys, we will use it to create a vote. Some of the user interface may have
changed since writing, so stay on your toes.

### Collecting Member Contacts

In an election, everyone gets only one ballot to fill out. This rules out
the 'anonymous link' feature, since we need to verify that the submitter
is both authorized to vote _and_ that they only vote once.

To solve this problem we will use Qualtrics to generate a unique voting link
for each voting member (remember, this includes advisors). We begin by
collecting a CSV of people who have voting rights, and later import that into
Qualtrics.

Find the included Node.js script to download the member list from Scoreboard into
a CSV. Make any adjustments now: be sure to remove anomalies, correct name
spellings, and add advisors.

In Qualtrics, click on the 'Contacts' link on the top menu bar. Click 'Create
Contact List', name the list, and click then upload the CSV file.

### Creating the Survey

Now we must create the election poll. In Qualtrics, click on the 'Projects' link
on the top bar, and click 'Create Project'. Select 'Blank Survey Project' and
give it a name. Qualtrics adds a default question, you can delete this by
hovering over the entry and clicking the red minus on the right.

I recommend adding a short text field at the top of the survey that contains
the following text (edit as needed):

> Use the following questions to rank your officer preference, with the most
> preferred at the top.

Do this by clicking the drop-down beside 'Create a New Question', and selecting
'Descriptive Text'.

We will now enter each of the positions and the candidates. For each position,
click the drop-down beside 'Create a New Question', and select 'Rank Order'.
Replace the question text with the position and the options with the candidates.
**Be sure to delete unused options!**. Qualtrics will literally insert 'Click
to write item 3' as an option otherwise. Do this by clicking the option text,
click the drop-down that appears, and clicking 'Remove Item'.

When you are finished adding the candidates, we can now apply the randomizer.
This ensures fairness. On each question, click the gear icon, select
'Randomization', and select 'Randomize the order of all choices'. A shuffle
icon should appear.

We will now secure the submission process. Click the 'Survey Options' button
near the top. Select the option 'By Invitation Only'. Select the option
'Prevent Ballot Box Stuffing'. Click Save.

When you are done, click 'Preview' to check your work.

### Generating Unique Links

While on the project page for your survey, click 'Distributions'. Click
'Generate a trackable link for each contact'. Select your contact list from
the drop-down (ProTip: I start by just generating one for just myself and
following the following instructions below to send it to myself). Click
'Generate Links'. Do not worry, this will not email anybody. Save the CSV file
it generates. This contains the generated links.

### Emailing Voting Links

I use a [mail merge](https://en.wikipedia.org/wiki/Mail_merge) to email the links.
There is various software to accomplish this task, the one I used was was a
Google Sheets plug-in named GSM MailMerge. See thier documentation for usage.
The short story is: compose a draft message in gmail. Use {FirstName} {LastName}
{Link} and {Email} as placeholders. In Sheets, select all of your data except
for the top (heading) row. Click 'Add-Ons' > 'GSM MailMerge' > 'Email Selected
Addresses'.

### Tallying Results

To download the results use Qualtrics and navigate to your survey's page.
Click on the 'Data & Analysis' header. Click 'Export & Import'. **Click 'More
Options' and click 'Export viewing order data for randomized surveys'**.
Qualtrics doesn't record a ranked choice if you don't reorder it, so be sure
to select that option - it's used in the tally script.

Download the results and run the tallying script. See the script for details.
