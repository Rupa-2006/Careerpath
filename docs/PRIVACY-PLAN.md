# CareerPath privacy plan for under-18 students

**This is not legal advice.** It is a working plan written by an AI assistant to help you prepare for a talk with a lawyer. Please have a qualified Indian lawyer check it before you launch.

Checked on 4 November 2026. No code was changed.

## The short version

- India's data law treats everyone under 18 as a child. Before handling any personal data of a child, a site must get verifiable consent from a parent.
- This part of the law is expected to start around **13 May 2027**. That date is worked out from the Rules, not printed in them.
- CareerPath does not ask anyone's age today, and has no privacy notice and no parent step. Most of its users will be children, so sign-up as it stands would not meet the law once it starts.
- Most of CareerPath already works without an account. Only three things need one: saved quiz results, roadmap progress and the skills checklist.
- **Recommendation:** launch with no student accounts. Keep those three features on the student's own device, and keep logins for admins only. Add a parent consent step later only if students really need accounts.
- This lowers the risk a lot, but does not remove it. Some personal data can still reach the server, for example in what a student types into the assistant. A lawyer needs to look at that.

## How sure are we?

**Neither official copy could be opened.** The eGazette PDF gave a certificate error. The MeitY and PIB pages refused the request (403). So every legal point below comes from unofficial copies. Before relying on any wording, check it against the Gazette in a normal browser.

Each point has one of these labels:

| Label | Meaning |
|---|---|
| **[CODE]** | Confirmed. Read directly in this project's code |
| **[TEXT 2+]** | Wording of the law, and two or more unofficial copies agree. Not checked against the Gazette |
| **[TEXT 1]** | Wording of the law, seen in one unofficial copy only |
| **[REPORTED]** | Stated by commentators, not read in the legal text |
| **[OPEN]** | Our own reading, or simply not known. A lawyer should decide |

## 1. What accounts collect today

### Stored on the server, linked to a person

| Data | Required? | Where it comes from | Label |
|---|---|---|---|
| Email address, stored in lower case | Yes | Sign-up (`auth.py:61`, `Auth.tsx:58`) | [CODE] |
| Password, stored only as a hash | Yes | Sign-up (`auth.py:66`) | [CODE] |
| Name, up to 100 characters | Optional | Sign-up and Account page (`Auth.tsx:53`, `Account.tsx:63`) | [CODE] |
| State or Union Territory | Optional | Chosen on eligibility pages (`profile.py:14`, `useBackground.ts:59`) | [CODE] |
| Stream | Optional | Same as above | [CODE] |
| User ID, role, active flag, created and updated times | Automatic | `models.py`, class `User` | [CODE] |
| Login sessions: hash of the token, expiry, created time | Automatic | One per device (`auth.py:41`) | [CODE] |
| Roadmap steps marked done, with times | Optional | `UserStepProgress`, `journey.py:128` | [CODE] |
| Skills marked "learning" or "done", with times | Optional | `UserSkill`, `skills.py:57` | [CODE] |
| Quiz results: number answered, top courses, scores, and the text of the answers behind each course | Automatic when logged in | `QuizResult`, `journey.py:264` | [CODE] |

Quiz results deserve care. They show a young person's interests and likely direction, and every new attempt adds a row.

### Stored or handled without an account

| Data | What happens | Label |
|---|---|---|
| Hashed rate-limit keys | Built from IP address, plus email for logins. Removed after about a day. The hash has no secret key, so an IP address could be worked out from it by trying every address (`security.py:60`) | [CODE] |
| "Report a problem" messages | Free text kept with no link to an account, but a student could type their name or phone number (`journey.py:323`) | [CODE] |
| Assistant messages | Sent to the server, answered and not saved (`assistant.py`). Students can type anything, so they may reveal personal details | [CODE] |
| Quiz answers, State, stream and subjects | Sent to the server to work out a result. Not saved unless logged in (`journey.py:263`) | [CODE] |
| State, stream and subjects in web addresses | Used as URL settings (`useBackground.ts:69`), so they can appear in server logs | [CODE] |
| Server and host logs | The app adds no logging of its own, but web servers normally record IP addresses and web addresses. What the host keeps is unknown until a host is chosen | [OPEN] |

### Stored only on the student's device

State, stream, subjects and language sit in `localStorage`. A finished quiz sits in `sessionStorage` until sign-up. One login cookie lasts 14 days. **[CODE]**

### What it does not collect or do

No age or date of birth, phone number, address, school, marks, caste, income or photo. No advertising, analytics or outside fonts or scripts. Gemini wording is forced off in production. **[CODE]**

### Gaps in the current code

| Gap | Why it matters | Label |
|---|---|---|
| No age question | The site cannot tell who is a child | [CODE] |
| No privacy notice or consent step | A notice is needed before asking for consent | [CODE] |
| No parent step | Required for under-18s | [CODE] |
| No password reset | Someone who forgets their password cannot log in or delete their account, because deletion needs the password (`profile.py:47`) | [CODE] |
| Email is never verified | Anyone can sign up with someone else's email | [CODE] |
| No way to download your data | The right to a summary of your data has no feature behind it | [CODE] |
| Email cannot be changed | The Account page only edits the name | [CODE] |
| No published contact person or complaint route | Both are required | [CODE] |
| Admins can search all emails and names | Probably needed, but should be kept to very few people (`admin.py`) | [CODE] |
| An admin's change to a user leaves that user's ID in `update_history` after deletion | Small, but deletion is not fully complete (`admin.py`) | [CODE] |

Account deletion itself is good: it removes sessions, progress, quiz results and skills through database cascade rules. **[CODE]**

## 2. What the law says, as it applies to CareerPath

### Dates

| Stage | What starts | Date | Label |
|---|---|---|---|
| On publication | Definitions, the Data Protection Board | 13 November 2025 (one source says 14) | [TEXT 2+] for the rule, [REPORTED] for the date |
| After 1 year | Consent manager registration | About 13 November 2026 | Computed |
| **After 18 months** | **Most duties, including section 9 and Rules 3, 6 to 10, 12 and 14** | **About 13 May 2027** | Computed |

- Rule 1 says "eighteen months" after publication. It gives no calendar date. Every "13 May 2027" you see is someone's calculation. **[TEXT 2+]**
- The Rules are G.S.R. 846(E). A correction, G.S.R. 892(E), followed in December 2025; copies disagree on whether it is dated the 10th or 11th. **[REPORTED]**
- In January 2026 the press reported a plan to shorten 18 months to 12 for Significant Data Fiduciaries, which are large notified companies. No change had been found as of 28 October 2026. **[REPORTED]** Check again before launch.
- A Removal of Difficulties Order, S.O. 5458(E), dated 5 October 2026, adds the word "of" to section 9(1). Commentators call it a drafting fix that does not change parental consent or the start date. **[REPORTED]** The Order's text was read in unofficial copies only.

### The children's rules

- A child is anyone who has not turned 18. **[TEXT 1]** So 16 and 17 year olds count fully. There is no lower age for career sites.
- **Section 9(1):** verifiable parental consent before processing *any* personal data of a child. **[TEXT 2+]** The word "any" matters: this is not limited to accounts.
- **Section 9(2):** no processing likely to harm a child's well-being. **[TEXT 2+]**
- **Section 9(3):** no tracking, behavioural monitoring or targeted advertising aimed at children. **[TEXT 2+]** Consent does not appear to lift this duty; section 9 has no such wording. CareerPath has no ads or analytics, which helps. Whether quiz results and saved progress count as "behavioural monitoring" is **[OPEN]**.
- **Parents have rights too.** "Data Principal" includes a child's parent, so a parent can use the child's rights. **[TEXT 1]**
- **Maximum penalty** for breaking the children's rules is ₹200 crore, and ₹250 crore for failing to keep data safe. These are upper limits. **[TEXT 1]**, and one law firm's summary gives the same figures. How a very small project would be treated is **[OPEN]**.

### Rule 10: how parental consent works

**[TEXT 2+]** for the rule itself, **[TEXT 1]** for the examples.

- The site must take suitable technical and organisational steps so that a parent's verifiable consent comes *before* any processing of the child's data.
- It must take care to check that the person claiming to be the parent is an adult, and identifiable where a law needs that.
- It can check using either reliable identity and age details it already holds, or details given voluntarily by that person, or a virtual token from an authorised body. DigiLocker is named as one route.
- The Rule's four examples all involve creating a child's account:
  - If the parent already has an account with verified details, the site checks those.
  - If the parent has no account, the site checks against details issued by a body the law or government trusts with them, or a token linked to those details.

CareerPath holds no parent details. So every parent would fall into the second, harder case. **[OPEN]** It is unclear whether a parent simply typing their own details would be enough. The Rule seems to allow it, but the examples point to government-backed details.

The Rule talks about checking that the person is an adult. It does not clearly say the site must prove they are really this child's parent. **[OPEN]**

### Fourth Schedule: the exceptions

**[TEXT 2+]** Four copies agree on Parts A and B.

| Exception | Does it help CareerPath? |
|---|---|
| Part A: hospitals, clinics, health professionals | No |
| Part A: educational institutions, only for tracking and monitoring for their own educational activities or the safety of enrolled children | Probably not. An educational institution is defined as a place of learning that imparts education. CareerPath gives guidance and enrols no one. Even for a real school, this covers tracking and monitoring, not everything. **[OPEN]** |
| Part A: crèches, day care, school transport | No |
| Part B: duties under law, and benefits under law or using public funds | No, unless a government body runs it one day |
| Part B: creating an email-only account | No. CareerPath accounts do far more than email |
| Part B: real-time location for safety | No |
| Part B: keeping harmful content from a child | Possibly, for a safety filter, but not for accounts |
| **Part B: confirming a user is not a child, and doing the Rule 10 checks** | **Yes.** An age question and parent checks may be done without parental consent, but only as far as needed |

**Other things that do not appear to help:**

- Being small. Section 17(3) lets the government relieve startups from some duties, but section 9 is not on that list. **[TEXT 1]**
- Section 9(5), which lets the government lower the age for a site proven "verifiably safe". We found no such notice, and no rule explains how to apply. **[OPEN]**
- The research exception in Rule 16. It covers research, archiving and statistics, not a career service. **[TEXT 1]**

### Other duties for any site that keeps personal data

All **[TEXT 1]**. These start at the same time, and cover adults as well.

| Duty | Source | What CareerPath would need |
|---|---|---|
| Plain notice listing each kind of data and each purpose, with links to withdraw consent, use rights and complain to the Board | Section 5, Rule 3 | A notice, available in English and Indian languages under the Eighth Schedule, so Telugu and Hindi too |
| Consent must be a clear action, and withdrawing must be as easy as giving it | Section 6 | A real tick or button, and an easy way to withdraw |
| Security, including encryption or masking, access control, logs and backups | Section 8, Rule 6 | Much already exists. Add a written contract with the host |
| Breach notice: tell affected people and the Board without delay, with a full report to the Board within 72 hours | Rule 7 | A written plan |
| Keep personal data, traffic data and logs for at least one year | Rules 6 and 8(3) | See the conflict below |
| Publish a contact person | Rule 9 | A name or role and an email address |
| Publish how to use your rights, and answer complaints within 90 days at most | Rule 14 | A rights page and a complaints inbox |
| Access, correction, erasure and nominating someone | Sections 11 to 14 | Data download, email change, a nomination option |

**A conflict to solve.** The law says to erase data when consent is withdrawn, but Rule 8(3) says keep data and logs for at least a year. Rule 8(3) is tied to government purposes in the Seventh Schedule, yet its examples are ordinary businesses. CareerPath deletes everything at once and clears rate-limit records after a day. Which rule wins, and whether a deleted child's data must be kept, is **[OPEN]**.

**Disability.** Section 9(1) also covers adults with disabilities who have a lawful guardian, and Rule 11 explains how to check the guardian. **[TEXT 2+]** for section 9, **[TEXT 1]** for Rule 11. So "18 and over" accounts are not free of this duty.

## 3. Options

### Option A: keep accounts as they are

Not acceptable once section 9 starts, because children could sign up with no parental consent. **Rejected.**

### Option B: accounts for over-18s only

Add a required "Are you 18 or over?" question. Under-18s use the site without saving.

- **For:** small change. Asking is allowed by Part B.
- **Against:** the site is built for Class 12 students, so a yes/no tick is weak. Many 16 and 17 year olds would just tick yes. If you know your audience is mostly children, a tick may not count as due care. **[OPEN]**
- **Also needed:** every duty in the table above.

### Option C: a parent consent step

Under-18s can have accounts after a parent is checked. The cleanest form is the parent starting the account (Cases 3 and 4 in Rule 10), because then no child data is stored before consent.

- **For:** students keep progress across devices, and parents are involved.
- **Against:**
  - The check needs government-backed details or a token, probably through DigiLocker. Whether a small project can join, and what it costs, is **[OPEN]**.
  - Many students would drop out because a parent is busy, away or does not use digital ID.
  - Holding parents' details adds risk. Never store ID copies or Aadhaar numbers.
  - It needs parent screens, withdrawal, and a plan for the day a student turns 18.
  - Every duty in the table above still applies.
- **Effort:** the largest option by far.

### Option D: every feature works without an account

Close student sign-up. Keep saved quiz results, roadmap progress and the skills checklist in the browser's `localStorage`, the same way State and subjects are kept today. Logins remain for admins only.

- **For:**
  - The server stops holding student emails, names, quiz results and progress. A leak would expose far less.
  - Nothing stops a student from starting. No parent is needed and it works for everyone, which suits budget phones and first-time users.
  - Most duties become much smaller, with little left to access, correct or erase.
  - The change is modest, because the pattern already exists in `useBackground.ts`.
- **Against:**
  - Progress does not follow the student to another phone, and is lost if browser data is cleared.
  - On a shared family phone, others can see it.
  - It does not bring the risk to zero, because section 9(1) says *any* personal data. Assistant messages, report messages and IP addresses may still count. **[OPEN]**
  - Whether data kept only on the student's device counts as processing by CareerPath is **[OPEN]**. We think it is a good sign that CareerPath never receives it, but a lawyer must say.

### Option E: run it through schools

A school might carry the duties and CareerPath would act for it. One lawyer's article suggests this for ed-tech that works only for institutions. **[REPORTED]** But the school exception is narrow, this needs signed deals with each school, and it cannot serve students directly. Not a launch plan.

### Comparison

| | A: as is | B: 18+ only | C: parent step | D: no student accounts |
|---|---|---|---|---|
| Meets section 9 for accounts | No | Doubtful | Yes, if done well | Yes, none exist |
| Student data on server | Most | Less | Most | Least |
| Easy for a 16 year old | Yes | Cannot save | Hard | Yes |
| Progress across devices | Yes | Adults only | Yes | No |
| Work to build | None | Small plus all duties | Very large | Modest |
| Fits a one-person project | No | Partly | No | Yes |

## 4. Recommendation

**Choose Option D for launch. Keep Option C as a later step, only if students clearly need accounts.**

The main reason is simple: the people CareerPath is for are mostly the people the law protects most. Holding less of their data is safer than building a heavy system to hold it properly. Removing an account also removes most of the duties that a one-person project would struggle to meet.

Do not launch with under-18 accounts just because May 2027 is still far off. Those accounts would then need parental consent, and how old accounts are treated for children is **[OPEN]**.

### Suggested order of work

These are for later, after you agree with this plan. No code has been changed.

1. Talk to a lawyer using the questions below.
2. Move saved quiz, roadmap progress and skills to the browser.
3. Close student sign-up, and keep admin login.
4. Add a short note above the assistant and report boxes: please do not type your name, phone number or other private details.
5. Remove emails and phone numbers from report messages before saving, as `scrub` in `assistant_ai.py` already does for AI text.
6. Use a secret key when hashing rate-limit keys.
7. Move State, stream and subjects out of web addresses, or make sure logs drop them.
8. Pick a host with a short log period, and sign its data terms. Check Rule 8(3) advice first.
9. Publish a plain privacy page in English, with a contact email and how to complain.
10. Keep ads, analytics and trackers out. Any AI provider must be checked first, because student text would be sent to it.
11. Write a one-page plan for what to do in a data breach.
12. Check the Gazette again before launch, and again before May 2027.

## 5. Questions for a lawyer

**Who is responsible**

1. Who is the Data Fiduciary if a student runs this alone: the person, or should a company or trust be set up? If the builder is under 18, does that change anything?
2. Is there any relief for very small or non-profit projects?

**No-account design**

3. If nothing is stored against a person, are IP addresses, typed assistant messages and report messages personal data of a child under section 9(1)?
4. If so, is parental consent needed before a child uses the assistant, even though nothing is saved?
5. Does data kept only in the student's browser count as processing by CareerPath?
6. Is a clear "do not type personal details" note enough, along with removing them?

**Age and consent**

7. Is a yes/no age question enough for a site aimed at Class 12 students? What due care is expected?
8. Under Rule 10, can a parent's own typed details be enough, or is a government-backed check needed in practice?
9. Must a site prove the parent–child relationship, or only that the parent is an adult?
10. Can a small project use DigiLocker for this, and how? Would a consent manager help?
11. What must happen when a student turns 18?
12. What must a site do on discovering a child lied about their age?

**Meaning of the rules**

13. Are the quiz, its recommendations and saved progress "tracking or behavioural monitoring"?
14. Could CareerPath ever count as an "educational institution" under the Fourth Schedule?
15. Does Rule 8(3) one-year retention apply to CareerPath, given the link to the Seventh Schedule? How does it fit with deletion on request, especially for children?
16. Is 13 May 2027 the correct date, and how are accounts created before that date treated?
17. Does the same apply to adults with lawful guardians, and how should a site handle that?

**Other laws**

18. Which other laws apply, such as the IT Act, consumer law or rules on advice to minors? They were not reviewed here.
19. Is the assistant's self-harm response safe and suitable under section 9(2)?

## 6. What was and was not checked

**Read in this project:** `auth.py`, `profile.py`, `Auth.tsx`, `Account.tsx`, plus the models, schemas, security, config, admin, journey, skills and assistant code and browser storage code.

**Could not be opened:** the eGazette copy of the Rules, MeitY copies of the Rules, Act and Order, and the PIB release. So the PIB timeline in earlier notes was not confirmed from PIB itself.

**Not reviewed:** cross-border transfers (section 16), the full Act and Rules, other Indian laws, and Stepora. Stepora is the same product and is still online, so the same questions apply to any personal data it keeps.

**Unofficial copies can be wrong or out of date.** Treat every **[TEXT]** label as "very likely, but check the Gazette".

## Sources

Official copies to check by hand (these did not open here):

- [Rules, eGazette](https://egazette.gov.in/WriteReadData/2025/267650.pdf)
- [Rules, MeitY](https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf)
- [Commencement notification G.S.R. 843(E), eGazette](https://egazette.gov.in/WriteReadData/2025/267647.pdf)
- [The Act, eGazette](https://egazette.gov.in/WriteReadData/2023/248045.pdf)
- [Removal of Difficulties Order, MeitY](https://www.meity.gov.in/static/uploads/2026/10/daf495a7b5798a3dfa72a944b51fc176.pdf)

Unofficial copies of the legal text that were read:

- [Rules, CADP](https://cadp.in/resources/official-texts/dpdp-rules-2025/)
- [Order, CADP](https://cadp.in/resources/official-texts/dpdp-order-removal-of-difficulties-2026/)
- [Fourth Schedule, dpdprules.org](https://dpdprules.org/rules/fourth-schedule)
- [Fourth Schedule, Privacy Law Hub](https://privacylawhub.com/bare-acts/dpdp-rules-2025/schedule-iv-fourth-schedule-exemptions-from-section-9-1-and-9-3-)
- [Section 9, dpdprules.org](https://dpdprules.org/act/9)
- [Rule 10](https://www.dpdpa.in/dpdpa_rules_2025/Rule_10.htm) and [Rule 12 with Fourth Schedule](https://www.dpdpa.in/dpdpa_rules_2025/Rule_12.htm), dpdpa.in
- Act on dpdpa.in: [chapter 1](https://www.dpdpa.in/chapter1.htm), [chapter 2](https://www.dpdpa.in/chapter2.htm), [chapter 3](https://www.dpdpa.in/chapter3.htm), [chapter 4](https://www.dpdpa.in/chapter4.htm), [Schedule](https://www.dpdpa.in/schedule1.htm)

Commentary:

- [The 18 to 12 month proposal, dpdprules.org](https://dpdprules.org/blog/dpdp-18-months-to-12-months-proposal)
- [Removal of Difficulties Order, dpdprules.org](https://dpdprules.org/blog/dpdp-removal-of-difficulties-order-2026)
- [Compliance timeline, MirvoLegal](https://www.mirvolegal.com/insights/dpdp-rules-2025-compliance-timeline/)
- [Ed-tech and child data, LiveLaw](https://www.livelaw.in/articles/dpdp-child-data-rules-demand-edtech-platforms-555317)
- [Report on the proposed shorter timeline, Business Standard](https://www.business-standard.com/technology/tech-news/meity-may-cut-compliance-timeline-for-key-dpdp-rules-to-12-months-126012201293_1.html)
