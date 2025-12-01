# Testing Guide - Auto-Ops-AI 🧪

## Sample Questions to Test the System

### 1. **Greeting Test** 👋
**Purpose**: Test initial greeting and conversation start

**Try these**:
- `Hi`
- `Hello`
- `Hey there`

**Expected**: Friendly greeting with list of services offered

---

### 2. **Network Issues** 🌐

#### Simple VPN Problem
```
My VPN is not connecting
```

**Expected Flow**:
1. Bot asks: "When did this start?" and "Are you on WiFi or ethernet?"
2. You answer: "Started this morning, I'm on WiFi"
3. Bot provides troubleshooting steps:
   - Reconnect WiFi
   - Flush DNS cache
   - Restart computer

#### Urgent VPN Issue with Meeting
```
VPN won't connect and I have a meeting in 20 minutes
```

**Expected**: 
- Auto-detected urgency (meeting in 20 min)
- HIGH priority ticket
- Faster troubleshooting without many questions

#### Critical Network Down
```
The entire office network is down! This is urgent!
```

**Expected**:
- CRITICAL priority
- Immediate escalation to human team
- Multiple users affected detection

---

### 3. **Performance Issues** 🐌

#### Slow Computer
```
My computer is really slow and keeps freezing
```

**Expected**:
1. Questions about when it started, frequency
2. Steps: Check Task Manager → Close programs → Restart
3. After each step, bot asks if it worked

#### With Deadline Urgency
```
My laptop is extremely slow and I need to finish a presentation in 30 minutes
```

**Expected**:
- Urgency detected (deadline in 30 min)
- HIGH priority
- Quick troubleshooting steps

---

### 4. **Software/Email Issues** 📧

#### Outlook Problem
```
Outlook is not sending emails
```

**Expected**:
1. Questions: When started? Error messages?
2. Answer: "Started today, no error message"
3. Troubleshooting steps from knowledge base (if similar issue found)

#### With Error Message
```
I can't send emails in Outlook. It says "Error 550: Mailbox unavailable"
```

**Expected**:
- Error message extracted and logged
- Specific troubleshooting for SMTP errors
- Possible escalation if complex

---

### 5. **Access/Login Issues** 🔒

#### Password Problem
```
I can't login to my account, it says password is incorrect
```

**Expected**:
1. Questions: When did this happen? Caps Lock off?
2. Steps: Re-login → Password reset escalation
3. Quick escalation to IT for password reset

#### Locked Account
```
My account is locked and I need access urgently
```

**Expected**:
- HIGH priority (blocking work)
- Immediate escalation to human
- Password reset ticket created

---

### 6. **Hardware Issues** 🖥️

#### Monitor Problem
```
My external monitor is not working
```

**Expected**:
1. Questions: When started? Cables checked?
2. Steps: Check cables → Restart → Driver update
3. Possible escalation if requires physical inspection

#### Blue Screen of Death
```
My computer keeps showing a blue screen and restarting
```

**Expected**:
- CRITICAL priority (BSOD keyword)
- Immediate escalation
- Hardware category detected

---

### 7. **Data Loss (Critical)** 🚨

```
I accidentally deleted important client files!
```

**Expected**:
- CRITICAL priority (data_at_risk detected)
- Immediate escalation to specialist team
- No troubleshooting steps (needs expert)

```
All my files disappeared from my desktop
```

**Expected**:
- CRITICAL priority
- Data recovery escalation
- Urgent ticket creation

---

### 8. **Multi-Turn Conversation Test** 🔄

**Full Workflow Test**:

1. **Start**: `Hi`
2. **Bot**: "What problem are you experiencing?"
3. **You**: `My internet is not working`
4. **Bot**: Asks questions (when started? frequency?)
5. **You**: `Started this morning, first time`
6. **Bot**: Provides Step 1 (reconnect WiFi)
7. **You**: `Didn't work`
8. **Bot**: Provides Step 2 (flush DNS)
9. **You**: `Still not working`
10. **Bot**: Provides Step 3 (restart)
11. **You**: `Still broken`
12. **Bot**: Escalates after 3 failed attempts

---

### 9. **Escalation Triggers** ⚠️

Test automatic escalation with these:

#### Security Issue
```
I think my computer has a virus, it's acting weird
```

**Expected**: Immediate escalation (security keyword)

#### Multiple Failed Attempts
- Try 3 troubleshooting steps
- Say "still not working" each time
- Bot should escalate after 3rd failure

#### High Frustration
```
This is the third time this week! Nothing works!
```

**Expected**: Frustration detected → Faster escalation

---

### 10. **Priority Testing** 📊

#### Low Priority (Contractor + Non-urgent)
```
Register as: Contractor tier
Issue: "My mouse wheel is a bit sticky"
```

**Expected**: LOW priority

#### Medium Priority (Staff + Medium urgency)
```
Register as: Staff tier
Issue: "Chrome is running slow"
```

**Expected**: MEDIUM priority

#### High Priority (Manager + Urgent)
```
Register as: Manager tier
Issue: "I can't access the database urgently"
```

**Expected**: HIGH priority

#### Critical Priority (Any tier + Critical keywords)
```
Register as: Any tier
Issue: "System crashed, data might be lost, client demo in 15 minutes"
```

**Expected**: CRITICAL priority

---

## Test Scenarios by User Type

### Manager Test (High Priority)
1. Register as Manager
2. Say: `My email is down and I have a board meeting in 30 minutes`
3. **Expected**: CRITICAL priority, immediate help

### Staff Test (Medium Priority)
1. Register as Staff
2. Say: `My computer is slow`
3. **Expected**: MEDIUM priority, normal troubleshooting

### Contractor Test (Lower Priority)
1. Register as Contractor
2. Say: `My keyboard is not working properly`
3. **Expected**: Priority adjusted based on tier

---

## Embedding Similarity Test 🧠

These should find similar issues from the knowledge base:

1. `VPN authentication fails` → Should match VPN KB articles
2. `Computer boots slowly` → Should match performance KB articles
3. `Cannot send emails` → Should match Outlook KB articles
4. `Blue screen error` → Should match hardware/crash KB articles

**Check**: Bot should say "💡 I found a very similar issue (XX% match)"

---

## Edge Cases to Test

### Empty/Short Messages
- `ok`
- `yes`
- `no`

**Expected**: Bot asks for clarification

### Multiple Issues at Once
```
My VPN is down, computer is slow, and I can't print
```

**Expected**: Bot focuses on first/most critical issue

### Already Tried Common Steps
```
My internet is down. I already tried restarting my computer and router.
```

**Expected**: Bot detects "already tried restart" and skips that step

---

## Success Metrics to Check

✅ **Conversation Flow**: No infinite question loops  
✅ **Question Limit**: Max 2 rounds of questions before troubleshooting  
✅ **Escalation**: Triggers after 3 failed attempts  
✅ **Priority**: Adjusts based on urgency keywords  
✅ **Similarity**: Finds KB articles with >70% match  
✅ **Ticket Creation**: Includes all conversation context  
✅ **Time Detection**: Parses "30 minutes", "this morning", etc.  
✅ **Error Extraction**: Captures quoted error messages  

---

## Quick Test Checklist

- [ ] Register new user (all 3 tiers)
- [ ] Login successfully
- [ ] Send greeting ("Hi")
- [ ] Describe simple issue
- [ ] Answer diagnostic questions (max 2)
- [ ] Receive troubleshooting steps
- [ ] Test "it worked" response
- [ ] Test "still broken" response
- [ ] Trigger escalation (3 failures)
- [ ] Test urgent scenario (meeting in X min)
- [ ] Test critical scenario (data loss)
- [ ] Check ticket creation
- [ ] View ticket list
- [ ] Logout

---

## Performance Benchmarks

**Expected Response Times**:
- Greeting: < 1 second
- Question generation: < 2 seconds
- Troubleshooting steps: < 3 seconds (with embedding search)
- Ticket creation: < 1 second
- Escalation decision: < 1 second

**Embedding Similarity**:
- VPN issues: 75-90% match
- Performance issues: 70-85% match
- Software issues: 65-80% match

---

## Troubleshooting Test Issues

### If bot keeps asking questions forever:
**Fixed!** Now limited to 2 question rounds

### If no similar issues found:
- Check if Google API key is valid
- Verify dataset loaded (2,083 tickets)
- Test with exact KB article keywords

### If escalation doesn't trigger:
- Try saying "still broken" 3 times in a row
- Use keywords: "critical", "urgent", "data loss"
- Set meeting time < 15 minutes

### If priority is wrong:
- Check user tier (manager > staff > contractor)
- Use urgency keywords ("urgent", "asap", "critical")
- Mention time constraints ("meeting in X minutes")

---

**Happy Testing! 🎉**
