- [x] Implement file upload functionality via bot
- [x] feat: Implement user creation with Telegram ID and initial credit
  - [x] - Update the `create_user_via_tgid` endpoint to properly handle and store the `telegram_id`.
  - [x] Ensure users created via Telegram bot are initialized with 10 credits.
  - [x]  Adjust user model to include `telegram_id` in database schema.
- [x] Develop logic for uploading a single file by user from tg-bot and deducting balances accordingly before file downloaded by bot
  - [x] created a pricing table and made endpoints to it to create and receive information for calculating the cost of a file in tg bot
  - [x] updated balance request command from /balance_{id_in_database} to /balance using user id inside tg
  - [x] access to transactions made with user's tg id via bot
  - [x] made function handle_file_upload, which calculates the cost of the file by the formula buffer_cost = estimated_cost * (1 + (pricing['extra_buffer_percentage'] / 100)), then this buffer_cost is subtracted from the balance, then the file is downloaded, then the adjustment is made (balance replenishment) without extra_buffer_percentage.
  - [x] added rounding of calculations to 2 decimal places, so as not to count at a loss to oneself
  - [x] created check - if there are not enough funds on the balance - the file is not uploaded anywhere from the dialog with the tg-bot.


- [ ]Implement 2 file upload functionality via bot
- [ ] Develop logic for uploading 2 file and deducting balances accordingly
