# Assetify by GLOIFY — Complete User Guide

Assetify keeps one record of every office device: what it is, where it is, who has it, when it
was bought, when its warranty ends, and everything that has ever happened to it.

**App address:** https://assetify-six.vercel.app

This guide walks through every page, every button and every field. Read **Part 1** once; after
that, jump to whatever page you need using the table of contents.

---

## Contents

1. [Getting started](#1-getting-started)
2. [How the screen is laid out](#2-how-the-screen-is-laid-out)
3. [Tips that apply to every page](#3-tips-that-apply-to-every-page)
4. [Dashboard](#4-dashboard)
5. [Assets (the device list)](#5-assets-the-device-list)
6. [Add Device](#6-add-device)
7. [Viewing a device (the details popup)](#7-viewing-a-device-the-details-popup)
8. [Editing a device](#8-editing-a-device)
9. [Check Out (give a device to someone)](#9-check-out-give-a-device-to-someone)
10. [Check In (take a device back)](#10-check-in-take-a-device-back)
11. [People](#11-people)
12. [Locations](#12-locations)
13. [Latest Operations](#13-latest-operations)
14. [Warranty Nearby Expiry](#14-warranty-nearby-expiry)
15. [Notifications](#15-notifications)
16. [Audit Trail](#16-audit-trail)
17. [Profile, passwords and logging out](#17-profile-passwords-and-logging-out)
18. [Users](#18-users)
19. [Device life cycle (statuses)](#19-device-life-cycle-statuses)
20. [Recommended routines](#20-recommended-routines)
21. [Messages you may see and what to do](#21-messages-you-may-see-and-what-to-do)
22. [Glossary](#22-glossary)

---

## 1. Getting started

### 1.1 Signing in

1. Open https://assetify-six.vercel.app. You land on the **Sign in** page (logo, "Assetify by
   GLOIFY", and a card with two boxes).
2. In **Username or email**, type your username (for example `sai` or `girish`) or your full
   email address. Capital letters don't matter.
3. In **Password**, type your password.
4. Click **Sign in**. You arrive on the **Dashboard**.

If the details are wrong you stay on the page and see a red message: *Invalid email or password.*
Check for a typo and try again.

There is **no sign-up page**. Only the accounts that already exist can sign in.

### 1.2 Automatic sign-out

If you do nothing for **30 minutes**, the app signs you out for safety. The next click takes you to
the Sign in page with a yellow notice saying your session expired. Sign in again and you are
taken back to where you were. Anything you were typing and had not saved is lost, so save forms
promptly.

### 1.3 First thing to do: change your password

Your account starts with a temporary password. Change it straight away:

1. Click your **name** at the top right → **Change password** (see [section 17](#17-profile-passwords-and-logging-out)).
2. Enter the current password once, the new password twice, and click **Change password**.

---

## 2. How the screen is laid out

Every page after sign-in has the same frame.

### 2.1 Left sidebar (the main menu)

The sidebar shows the app logo at the top and the menu below. The page you are on is
highlighted. On a phone or narrow window the sidebar is hidden; tap the **menu (☰) button** at
the top left to open it, and the **✕** button to close it.

| Section | Menu item | Takes you to |
|---|---|---|
| (top) | Dashboard | Overview with totals and charts |
| **Assets** | Assets | The full device list |
| | Check In | Return a device |
| | Check Out | Give a device to a person |
| | Add Device | Register a new device |
| **Directory** | Add People | The people list and the add-person form |
| | Add Location | The locations list and the add-location form |
| **Monitor** | Latest Operations | The 100 most recent actions |
| | Warranty Nearby Expiry | Devices whose warranty is ending |
| | Notifications | Your alerts (a red number shows unread ones) |
| | Audit Trail | The complete history, with filters |
| **Account** | Users | The accounts that can sign in |
| | Profile | Your account details |

### 2.2 Top bar

From left to right:

- **Menu button (☰)** — phones and small windows only; opens the sidebar.
- **Page path** — a small label showing where you are.
- **Day/night switch** — click it to flip between light and dark mode. The app remembers your
  choice on that browser.
- **Bell (🔔)** — opens Notifications. A red number on the sidebar's Notifications item shows
  how many are unread; it refreshes by itself every minute.
- **Your name** — a menu with **Profile**, **Change password** and **Logout**.

### 2.3 Page header

Under the top bar each page has a **title**, a **one-line description**, and on the right the
**main action buttons** for that page (for example *Add Device* on the Assets page).

---

## 3. Tips that apply to every page

- **Fields marked \*** are required. If something is missing or wrong, the form stays open and
  each problem is shown in red under its field (and sometimes in a red box at the top). Fix it and
  save again; nothing is lost.
- **Green/red pop-up messages** appear in a corner after you save, e.g. "Device added." They go
  away on their own.
- **Search boxes** filter the list as you type; there is no need to press Enter. The list
  updates after a short pause. Clear the box to see everything again.
- **Tables are paged, 25 rows per page.** Use the page controls under the table (previous / next /
  page numbers). Wide tables (like Assets) scroll sideways; drag or use the scroll bar at the
  bottom of the table.
- **Popups** (device details, check-out, check-in) open over the page. Close them with **Cancel**,
  **Close**, the **✕**, or by clicking outside.
- **Confirmation questions** ("Retire LT-0001?") appear before anything hard to undo. Choose OK to
  continue or Cancel to stop.
- **Dates** are shown like `14 Mar 2027`. **Times** are shown in Indian time (IST).
- **Nothing is permanently erased by accident.** Retired and deleted devices disappear from the
  working lists, but their history stays in the Audit Trail.

---

## 4. Dashboard

**Menu:** Dashboard (the first item in the sidebar, and the page you land on after signing in).

A live snapshot. Everything updates each time you open or refresh the page.

### 4.1 Buttons at the top right
- **Check Out** — shortcut to the Check Out page.
- **Add Device** — shortcut to the Add Device form.

### 4.2 The six number tiles
Each tile is **clickable** and takes you to the matching list.

| Tile | Counts | Click goes to |
|---|---|---|
| Total assets | Every active device (not deleted) | Assets |
| Available | Devices ready to hand out | Assets filtered to Available |
| Checked out | Devices currently with someone | Check In page |
| Maintenance | Devices being repaired | Assets filtered to Under maintenance |
| People | People who can be given devices | People |
| Locations | Saved locations | Locations |

### 4.3 Assets by status (doughnut chart)
Shows how all your devices split between **Available**, **Checked Out**, **Under Maintenance**
and **Retired**. Hover a slice to see its number. The coloured list under the chart gives the
exact counts. If there are no devices yet it shows "No assets found."

### 4.4 Check-outs and check-ins (14-day chart)
A chart of daily activity for the last 14 days: how many devices were handed out and how many
came back each day. Hover a point or bar for that day's numbers. Use it to spot busy days.

### 4.5 Assets by type
A chart that splits devices by type: Laptop, Desktop, Monitor, Mobile, Tablet, Printer, Network.

### 4.6 Warranty nearby expiry (table)
Devices whose warranty ends within 90 days (plus ones that ended within the last 30). The
heading says how many. Columns: Asset Tag ID, Brand / Model, Warranty Expiry, Days Remaining.
The coloured **Days Remaining** pill tells you urgency:
- **Blue** — more than 30 days left
- **Yellow** — 30 days or fewer
- **Red "Expired Nd ago"** — already out of warranty

For the complete list and exact colours, see [section 14](#14-warranty-nearby-expiry).

### 4.7 Latest operations (table)
The most recent actions across the app: Date & Time, Operation (e.g. Check-Out), Asset Tag ID,
Employee, and which User did it. For more detail go to [Latest Operations](#13-latest-operations).

### 4.8 Charts in dark mode
Charts recolour themselves when you flip the day/night switch.

---

## 5. Assets (the device list)

**Menu:** Assets → Assets. This is the home for finding and managing devices.

### 5.1 The status tiles
Five clickable tiles at the top: **All assets**, **Available**, **Checked out**, **Maintenance**,
**Retired**, each with its count. Click one to show only those devices.

### 5.2 Searching and filtering
- **Search box** — type anything: part of the **asset tag**, **serial number**, **brand**,
  **model**, a **status word** (such as "available" or "checked out"), or the **name of the person
  currently holding** the device. Results update as you type.
- **Filter by status** drop-down — choose a status, or "All statuses". It works together with the
  search box (for example: status = Checked out, search = "Asha").

If nothing matches you see "No matching records found."

### 5.3 The table
Scroll sideways to see all columns:

| Column | Meaning |
|---|---|
| Photo | Thumbnail of the device (a placeholder if none was uploaded) |
| Asset Tag ID | Your own unique label for the device |
| Description | Short description |
| Status | Coloured pill: Available (green), Checked Out (amber), Under Maintenance (blue), Retired (grey) |
| Brand, Model, Serial Number | As entered |
| Memory, Hard Disk, OS, OS Version, Processor | Specs (— if left empty) |
| Department | The department of the current/last person it was given to |
| Last Check-In | When it was last returned |
| Location | Where it is now (if checked out) |
| Purchase Date, Warranty Expiry | Dates |
| Actions | **View** and **Edit** |

### 5.4 The two row actions
- **View** (eye icon) opens the details popup ([section 7](#7-viewing-a-device-the-details-popup)).
- **Edit** (pencil icon) opens the edit page ([section 8](#8-editing-a-device)).

### 5.5 Add Device button
Top right; opens [Add Device](#6-add-device).

---

## 6. Add Device

**Menu:** Assets → Add Device (or the *Add Device* button on the Assets page or Dashboard).

Fill in the form and click **Add Device** at the bottom right. **Cancel** or **Back to Assets**
leaves without saving.

### 6.1 Fields

| Field | Required? | What to enter |
|---|---|---|
| **Asset Tag ID** | Yes | Your unique label, e.g. `LT-0042`. Must not already exist. Upper/lower case counts as the same. |
| **Asset Type** | Yes | Laptop, Desktop, Monitor, Mobile, Tablet, Printer or Network. |
| **Status** | Yes | **Available** (ready to use) or **Under Maintenance** (not ready). A new device can't start as checked out; use Check Out for that. |
| **Description** | Yes | Short text, e.g. "Dell Latitude 5440 – Finance". |
| **Brand** | Yes | e.g. Dell |
| **Model** | Yes | e.g. Latitude 5440 |
| **Serial No** | Yes | The manufacturer's serial number. Must not already exist. |
| OS | No | e.g. Windows 11 |
| OS Version | No | e.g. 23H2 |
| Processor | No | e.g. Intel i7-1355U |
| Memory | No | e.g. `16 GB` |
| Hard Disk | No | e.g. `512 GB SSD` |
| **Purchase Date** | Yes | Click the box and pick a date. |
| **Warranty Expiry** | Yes | Must be **on or after** the purchase date. |
| Last Password | No | The device's login/admin password, if you want it on record. It is **stored encrypted** and hidden on screen; see [reveal](#73-the-last-password-line). |
| Asset Photo | No | A **JPG, JPEG or PNG**, up to **4 MB**. Large images are shrunk automatically. Other file types are refused, even if renamed. |

### 6.2 When the save succeeds
You return to the Assets list with a "Device added" message, and a *Device Added* entry appears
in Notifications and the Audit Trail.

### 6.3 Common errors
- **"Asset Tag ID already exists."** — choose another tag (this also applies to devices that
  were deleted earlier).
- **"Serial number already exists."** — the same serial is already registered.
- **"Warranty expiry cannot be before the purchase date."** — fix the dates.
- Photo problems — see [section 21](#21-messages-you-may-see-and-what-to-do).

---

## 7. Viewing a device (the details popup)

Open it with **View** on the Assets, Check Out or Check In lists.

### 7.1 What it shows
- **Top:** photo, description and the status pill.
- **Details grid:** Brand, Model, Serial Number, Type, OS, OS Version, Processor, Memory, Hard
  Disk, Purchase Date, Warranty Expiry, Department, Location, Last Check-In Date, **Last Used By**
  and **Last Password**.
- **Current assignment** (yellow box, only when the device is checked out): the person's name,
  employee ID, mobile, email, the location, department, check-out date and the check-out notes.
- **Assignment history:** every time the device was given out — who, where, department, when it
  went out and who recorded it, when it came back and who recorded it ("Still out" if it hasn't),
  and the notes.

### 7.2 Buttons at the bottom
Which buttons appear depends on the status:

| Button | Appears when | What it does |
|---|---|---|
| **Edit** | Always | Opens the edit page. |
| **Send to maintenance** | Device is Available | Changes status to Under Maintenance. |
| **Mark available** | Device is Under Maintenance | Changes status back to Available. |
| **Retire** | Not checked out, not already retired | After you confirm, marks it Retired: no longer offered for check-out, but it stays in the records. |
| **Delete** | Not checked out | After you confirm, hides the device from every list. Use only for entries made by mistake. |
| **Close** | Always | Closes the popup. |

A device that is **checked out** can't be retired or deleted: check it in first.

### 7.3 The Last Password line
It shows `••••••••` and a **Reveal** link. Clicking **Reveal** shows the real password on screen.
Every reveal is written to the Audit Trail with your name and time, so only reveal when you
need it. If no password was stored it shows a dash.

---

## 8. Editing a device

**How to open:** Assets list → **Edit** on the device's row (or **Edit** inside the details popup).

The form is the same as Add Device, with these differences:
- The title reads "Edit <tag>".
- **Status is shown as plain text and cannot be changed here.** Use *Send to maintenance* /
  *Mark available* / *Retire* from the details popup.
- **Last Password:** leave it blank to keep the stored password; type a new one to replace it.
- **Asset Photo:** choosing a file **replaces** the current photo; leaving it empty keeps it.

Click **Save changes**. Every change is recorded in the Audit Trail with the old and new values
(you can open "Changes" there to see them). **Cancel** discards your edits.

---

## 9. Check Out (give a device to someone)

**Menu:** Assets → Check Out. Only **Available** devices are listed here.

### 9.1 Step by step

1. Open **Check Out**. The table lists available devices (Select box, Photo, Asset Tag ID,
   Description, Status, View).
2. Use the **search box** to find the device ("Search available assets…").
3. Tick the box in the device's row. Only one row can be ticked at a time; ticking another moves
   the tick. The **Check Out** button (top right), greyed out until now, becomes active.
   (**View** shows the device's full details first, if you want to double-check.)
4. Click **Check Out**. A popup opens titled "Check Out <tag>". The top half shows the device
   details for confirmation.
5. Fill in the form:
   - **Person** — choose from the list.
   - **Location** — choose where the device will be.
   - **Department** — type it, or pick a suggestion that appears from earlier entries.
   - **Check-Out Notes** — optional (for example "includes charger and bag").
6. Click **Check Out** (bottom right of the popup).

The popup then confirms, the device becomes **Checked Out**, and everyone gets a "Device Checked
Out" notification. It now appears on the Check In page.

### 9.2 The person or location isn't in the list
You don't have to leave the popup:
- Click **Add new person** under the Person box. A small form opens inside the popup: Name,
  Employee ID, Mobile, Email, Pincode, Location, Address. Click **Save person**; the new person
  is selected automatically. **Cancel** closes the little form.
- Click **Add new location** under the Location box, fill in the form, and click **Save
  location**; it is selected automatically.

### 9.3 Good to know
- A device can only be with **one person at a time**.
- If someone else checked it out a moment earlier, you will see "This asset is no longer
  available for check-out." Close the popup and refresh the list.
- If the popup shows a red error, nothing was saved; correct the field and click Check Out again.

---

## 10. Check In (take a device back)

**Menu:** Assets → Check In. Only **Checked Out** devices are listed.

1. Open **Check In** and find the device (search by tag, description or the **employee's name**).
2. Tick its box; the **Check In** button at the top right becomes active.
3. Click **Check In**. The popup shows who holds it, where, the department, and the
   check-out date. "Check-In Date" says it is recorded automatically when you confirm.
4. Type **Check-In Notes** if useful (for example "screen scratched", "returned with charger").
5. Click **Check In**.

The device becomes **Available**, the assignment is closed in its history, and the "Last Check-In"
date is updated. The Dashboard's *Checked out* tile also links here.

---

## 11. People

People are the employees you can give devices to.

**Menu:** Directory → Add People opens the **People** list.

### 11.1 The list
- **Search box:** name, employee ID, email or mobile.
- Columns: Name, Employee ID, Mobile, Email, Pincode, Location, Actions (**Edit**).
- **Add People** button (top right) opens the form.
- Shows "No people added yet." when empty.

### 11.2 Adding a person
Click **Add People**, fill in, click **Add Person**.

| Field | Notes |
|---|---|
| Name \* | Full name |
| Employee ID \* | Must be unique. "Employee ID already exists." means that code is taken. |
| Mobile Number \* | Digits only |
| Email Address \* | Valid email format |
| Pincode \* | Digits only |
| Location \* | Pick from your saved locations. If the list is empty, you'll see a warning: add a location first. |
| Address \* | Full address |

### 11.3 Editing a person
Click **Edit** on their row, change what you need, click **Save changes**.

Everyone gets a "New Employee" notification when a person is added.

---

## 12. Locations

Locations are the places where devices are kept or used (an office floor, a branch, a store room).

**Menu:** Directory → Add Location opens the **Locations** list.

### 12.1 The list
- **Search box:** name, building, area or district.
- Columns: Name, Floor, Building, Area, District, State, Pincode, Actions (**Edit**).
- **Add Location** button (top right).

### 12.2 Adding a location
Click **Add Location**, fill in all fields, click **Add Location**.

| Field | Notes |
|---|---|
| Name \* | Must be unique, e.g. "Head Office – Floor 2". |
| Floor \*, Building Name \*, Area \*, District \*, State \* | Text |
| Pincode \* | Digits only |

"A location with this name already exists." means pick a different name. To fix a typo, use
**Edit** on its row. Everyone gets a "New Location" notification.

---

## 13. Latest Operations

**Menu:** Monitor → Latest Operations.

A read-only table of the **100 most recent** actions on devices, people and locations:

| Column | Meaning |
|---|---|
| Date & Time | When it happened |
| Operation Type | Device Added, Device Updated, Check-Out, Check-In, Person Added, Location Added, Asset Retired, Asset Deleted |
| Asset Tag ID | Which device (if any) |
| Employee | The person involved |
| Location | The place involved |
| User | Who in the app did it |
| Notes | Extra details |

The **Full audit trail** button (top right) goes to the complete, filterable history.

---

## 14. Warranty Nearby Expiry

**Menu:** Monitor → Warranty Nearby Expiry.

Lists every device whose warranty ends **within the next 90 days**, plus any whose warranty ended
**in the last 30 days**, so you can renew or replace in time.

Columns: Asset Tag ID, Brand, Model, Serial No, Warranty Expiry, **Days Remaining**.

The Days Remaining pill:

| Pill | Meaning |
|---|---|
| Blue "45 days" | 31–90 days left: plan ahead |
| Yellow "20 days" | 11–30 days left: act soon |
| Red "7 days" | 10 days or fewer left: urgent |
| Red "Expired 3 days ago" | Warranty has ended |

"No upcoming warranty expirations." means everything is safe for now.

---

## 15. Notifications

**Menu:** Monitor → Notifications, or the **bell** in the top bar.

A feed of alerts, newest first. **Unread** ones are highlighted with a blue dot; read ones are
grey. Everyone with an account gets their own copy of each alert, so marking yours as read does
not change anyone else's.

### 15.1 What creates a notification

| Type | When |
|---|---|
| Device Added / Updated / Retired / Deleted | Someone does that to a device |
| Device Checked Out | A device is given to a person |
| New Employee / New Location | A person or location is added |
| **Warranty Expiring** | The daily check finds a warranty ending within 30 days (once at 11–30 days left, once at 0–10 days left) |
| **Warranty Expired** | A warranty ended 7–14 days ago (sent once) |

The warranty check runs automatically every day at about **8:00 AM IST**; you don't have to do
anything. Each alert is sent once per stage, so you won't be nagged repeatedly.

### 15.2 What you can do
- **Click the message text** — jumps to the related page (e.g. the device in Assets).
- **Mark read** (on a single alert) — removes its highlight.
- **Mark all as read** (top right) — clears the highlight on every alert.

The number on the sidebar bell disappears when everything is read.

---

## 16. Audit Trail

**Menu:** Monitor → Audit Trail.

The complete, permanent record of what happened in the app, newest first. Use it to answer "who
changed this, and when?".

### 16.1 Filters
A card at the top lets you narrow the list:
- **Module** — Assets, Checkout, Checkin, People, Locations, Users, and so on.
- **User** — a person who has an account.
- **From / To** — pick start and end dates.
- Click **Filter** to apply; **Reset** clears everything.

### 16.2 Columns
Date & Time, Module, Action (what was done), Asset (tag, if relevant), User, Remarks, and IP
address.

### 16.3 Seeing what changed
For edits, a small **Changes** link appears under Remarks. Click it to see each field as
`field: old value → new value`.

### 16.4 What gets recorded
Sign-ins and sign-outs (and failed sign-in attempts), adding/editing/retiring/deleting devices,
status changes, check-outs and check-ins, **password reveals**, people and location changes,
profile and password changes, and user activations/resets. Passwords themselves are never
written to the log.

---

## 17. Profile, passwords and logging out

Open your **name** at the top right for the quick menu, or choose **Profile** in the sidebar.

### 17.1 Profile page
Shows your **Name, Email, Role** and **Last Login** time, with three buttons:
- **Edit Profile**
- **Change Password**
- **Logout**

### 17.2 Edit Profile
Change your **Name** or **Email** and click **Save**. The email must not belong to someone else.
You can sign in with either your new email or your name (the name must be unique among
accounts for this to work smoothly).

### 17.3 Change Password
1. **Current password** — the one you use today.
2. **New password** — at least **8 characters**.
3. **Confirm new password** — type it again exactly.
4. Click **Change password**.

Your new password is stored securely (as a scrambled hash; nobody, including the administrators,
can read it back). It is yours alone from now on, and it will **not** be overwritten by
the setup scripts. Errors: "Current password is incorrect." or "Passwords do not match."

**Tips for a good password:** 12 or more characters, not used anywhere else, not a name or birthday.

### 17.4 Logout
Use **Logout** on the Profile page or in the top-right name menu. Always log out on shared
computers.

---

## 18. Users

**Menu:** Account → Users.

Lists the accounts that can sign in: **Name, Email, Role, Status** (Active/Inactive), **Last
Login**. The subtitle shows how many are active. There is **no "Add user" button**: accounts are
fixed, there is no sign-up.

### 18.1 Reset password
Click **Reset password** on a row, enter a new password (8+ characters), and click **Reset
password**. Use this when a colleague has **forgotten** theirs; they should then change it in their
Profile. It is recorded in the Audit Trail.

### 18.2 Deactivate / Activate
On other people's rows (never your own) you can **Deactivate** (after a confirmation) to stop that
account signing in, or **Activate** to allow it again. Nothing is deleted; their past actions stay
in the history.

---

## 19. Device life cycle (statuses)

```
        ┌──────────── Send to maintenance ───────────┐
        ▼                                             │
 Under Maintenance ── Mark available ──► AVAILABLE ◄──┘
                                           │  ▲
                                 Check Out │  │ Check In
                                           ▼  │
                                      CHECKED OUT
 AVAILABLE or UNDER MAINTENANCE ── Retire ──► RETIRED
```

| Status | Meaning | Shown in Check Out list? |
|---|---|---|
| **Available** | In the office and ready to give out | Yes |
| **Checked Out** | With a person | No (it's on the Check In list) |
| **Under Maintenance** | Being repaired or inspected | No |
| **Retired** | Out of service for good; kept for history | No |

Rules: a checked-out device can't be retired, deleted or sent to maintenance until it is checked
in. A device with an open assignment can never be given to a second person.

---

## 20. Recommended routines

**When a new device arrives**
1. Add Device → fill in everything, including serial, dates and a photo.
2. Check Out to the user if it is going straight to them.

**When someone joins**
1. Add People (make sure their location exists first).
2. Check Out their devices.

**When someone leaves or swaps a device**
1. Check In every device they hold, noting its condition.
2. If it needs repair, open it → **Send to maintenance**; later → **Mark available**.

**Weekly**
- Look at **Warranty Nearby Expiry** and plan renewals.
- Glance at **Notifications** and mark them read.

**When a device is scrapped or sold**
- Check it in, open it, and choose **Retire** (not Delete). The history is kept.

**When you find a duplicate entry made by mistake**
- Check it in if needed, then **Delete**.

**Checking who had a laptop in March**
- Assets → View on that laptop → read **Assignment history**.

---

## 21. Messages you may see and what to do

| Message | Meaning / fix |
|---|---|
| Invalid email or password. | Typo or wrong password. Ask another user to reset it under Users. |
| Your session expired… | 30 minutes of inactivity. Sign in again. |
| Asset Tag ID already exists. | Tags must be unique. Pick another, or search for the existing device. |
| Serial number already exists. | That serial is already registered (even on a deleted device). |
| Warranty expiry cannot be before the purchase date. | Correct the two dates. |
| Employee ID already exists. | That code belongs to another person. |
| A location with this name already exists. | Use a different name. |
| This asset is no longer available for check-out. | Someone else got there first, or its status changed. Refresh. |
| Only checked-out assets can be checked in. | The device isn't out. Refresh the list. |
| A checked-out asset cannot be retired/deleted. Check it in first. | Do a Check In, then retry. |
| Maintenance can only be toggled for available assets. | The device is checked out or retired. |
| Photo rejected / not a valid image | Use a real JPG or PNG under 4 MB. Renaming another file type won't work. |
| Current password is incorrect. / Passwords do not match. | Re-type carefully on the Change Password form. |
| 404 "page does not exist" | The link is old or mistyped. Use **Back to Dashboard**. |
| 500 "unexpected error" | Try again. If it repeats, send the **Request ID** shown on the page to whoever maintains the app. |
| The page looks stuck or empty | Refresh the browser (F5). If you were signed out, sign in again. |

**Forgot your password?** Ask the other account holder to open **Users → Reset password** for
you, then change it yourself in your Profile.

---

## 22. Glossary

| Term | Meaning |
|---|---|
| **Asset / Device** | Any tracked item: laptop, monitor, phone, printer, etc. |
| **Asset Tag ID** | Your unique label for a device (like `LT-0042`). |
| **Check Out / Check In** | Giving a device to a person / receiving it back. |
| **Assignment** | One period when a device was with one person. A device's list of assignments is its history. |
| **Retire** | Take a device out of service but keep its records. |
| **Delete** | Hide a mistaken entry from every list. |
| **Audit Trail** | The permanent log of who did what and when. |
| **Warranty window** | The 90 days before a warranty ends (and 30 days after) shown on the warranty pages. |
| **Session** | The time you stay signed in; ends after 30 minutes of inactivity or when you log out. |
| **Modal / popup** | The box that opens over the page for details, check-out and check-in. |

---

*Assetify by GLOIFY — internal tool. Keep your password private and log out on shared
computers.*
