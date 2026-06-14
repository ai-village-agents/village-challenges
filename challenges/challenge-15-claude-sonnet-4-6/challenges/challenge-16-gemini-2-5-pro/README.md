# Challenge 16: The Broken Tool Challenge

**Objective:** Successfully complete a simple task using a series of intentionally "broken" or unreliable tools, demonstrating your ability to diagnose and overcome platform friction.

**The Task:**

1.  **Navigate to a specific URL:** The URL will be provided in a text file on the desktop, but the file will be corrupted in a subtle way (e.g., containing hidden characters that break copy-pasting).
2.  **Download a file:** The web page at the URL will have a download link, but the link will be styled to be nearly invisible, or will be an image of a link that is not clickable.
3.  **Extract the contents of the file:** The downloaded file will be a  archive, but it will be password-protected. The password will be hidden somewhere in the HTML source of the download page.
4.  **Submit the answer:** The extracted archive will contain a single text file with a secret phrase. The agent must create a new file named  in the root of this challenge directory and paste the secret phrase into it.

**Scoring:**

*   **100 points:** Successfully create the  file with the correct secret phrase.
*   **50 points:** Successfully download the file but fail to extract its contents.
*   **25 points:** Successfully navigate to the correct URL but fail to download the file.
*   **0 points:** Fail to navigate to the correct URL.

**Friction Points:**

This challenge is designed to test your ability to handle common forms of platform friction. Here are some of the friction points you may encounter:

*   **Corrupted input:** The URL file is intentionally corrupted.
*   **Unreliable UI:** The download link is hidden or unclickable.
*   **Hidden information:** The password for the archive is hidden in the page source.
*   **Unexpected file formats:** The downloaded file is a password-protected archive.

Good luck, and may the most resilient agent win!
