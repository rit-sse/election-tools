/**
 * Finds all active members and creates a CSV file from them
 *
 * Usage:
 * 1. Run 'npm install'
 * 2. Run 'npm start'
 *
 * NOTE: Some of this is taken from OneRepoToRuleThemAll
 * See: https://github.com/rit-sse/OneRepoToRuleThemAll/blob/master/app/js/scoreboard/actions.js#L14
 */
const fs = require('fs')
const axios = require('axios')
const moment = require('moment')

const Client = require('sse-api-client').default
const API = new Client('https://sse.rit.edu/api/v2/')

API
  .Memberships
  .all({
    active: moment().toISOString() // We're looking for active memberships
  })
  .then((
    // Group Memberships by DCE
    // {
    //   abc1234: {
    //     fistName: '',
    //     lastName: '',
    //     count: 0,
    //     memberships: [
    //       {
    //         reason: '',
    //         committeeName: '',
    //         startDate: '',
    //         endDate: '',
    //       }
    //     ]
    //   }
    // }
    memberships => memberships.reduce((members, membership) => ({
      ...members,
      [membership.userDce]: {
        ...(members[membership.userDce] || {
          firstName: membership.user.firstName,
          lastName: membership.user.lastName
        }),
        count: ((members[membership.userDce] || {}).count + 1 || 1),
        memberships: [
          ...((members[membership.userDce] || {}).memberships || []),
          {
            reason: membership.reason,
            committeeName: membership.committeeName,
            startDate: membership.startDate,
            endDate: membership.endDate
          }
        ]
      }
    }), {})))
    .then(members => {
      const str = Object
        .entries(members)
        // Get all members' DCE and Name
        .map((entry) => {
          const dce = entry[0]
          const member = entry[1]
          return {
            dce: dce,
            firstName: member.firstName,
            lastName: member.lastName
          }
        })
        // Convert them into a CSV formatted string
        .reduce((accum, member) => `${accum}\n${member.dce},${member.lastName},${member.firstName}`, 'DCE,Last Name,First Name')

      // Write them to a CSV file
      fs.writeFile('active_members.csv', str, (err) => {
        if (err) console.error(err)
        console.log('Success! ✅')
        console.log("Active members written to file 'active_members.csv'")
      })
    })
