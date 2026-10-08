# Putting the new site live on HostGator

This replaces the WordPress site at independentclaimsconsultants.com with the new site. It takes about 30 minutes. Nothing is deleted: WordPress is moved into a backup folder, so you can switch back at any time.

**Email isn't affected.** This includes nic@…co.uk and andy@independentclaimsconsultants.com, because email isn't stored in the website folder. Don't change any DNS or **Email Accounts** settings, and keep the HostGator hosting active.

## Before you start

- Get the upload file `independentclaimsconsultants-site.zip`. To make a fresh one, run `python3 _build/package.py` and the zip appears in the repo folder.
- Log in to HostGator. From the Customer Portal, open **cPanel** for the hosting package that has independentclaimsconsultants.com.

## Step 1: Back up WordPress

1. In cPanel, open **Backup** (or **Backup Wizard**).
2. Download a **Home Directory** backup and a backup of the **MySQL database** for WordPress. Keep them somewhere safe.

## Step 2: Check the security certificate (HTTPS)

1. In cPanel, open **SSL/TLS Status**.
2. Check that `independentclaimsconsultants.com` and `www.independentclaimsconsultants.com` both have a green padlock.
3. If they don't, select them and click **Run AutoSSL**. Wait until they turn green before going on.

The new site sends every visitor to the `https://` address. This only works when the certificate is active.

## Step 3: Move WordPress out of the way

1. In cPanel, open **File Manager**.
2. Click **Settings** (top right), tick **Show Hidden Files (dotfiles)** and save.
3. Open **public_html**.
   - If independentclaimsconsultants.com is an add-on domain, open its own folder instead. **Domains** in cPanel shows which folder it uses.
4. Click **+ Folder** and create a folder called `old-wordpress`.
5. Select everything in the folder **except**:
   - `old-wordpress`
   - `.well-known`
   - `cgi-bin`
   - the folders of any other websites you host here
6. Click **Move**, enter the path of the `old-wordpress` folder, and confirm.

The WordPress files usually include `wp-admin`, `wp-content`, `wp-includes`, `index.php`, the `wp-*.php` files and `.htaccess`.

## Step 4: Upload the new site

1. Still in the website folder, click **Upload** and choose `independentclaimsconsultants-site.zip`.
2. When it finishes, go back to File Manager, right-click the zip and choose **Extract** into the same folder.
3. Check that `index.html`, `.htaccess`, `assets` and the page folders (`about`, `claims` and so on) are directly inside the website folder, not inside a subfolder.
4. Delete the zip file.

## Step 5: Check it works

Open these in your browser. Use a private window so you don't see a cached copy.

| Address | You should see |
| --- | --- |
| https://independentclaimsconsultants.com | The new homepage |
| http://www.independentclaimsconsultants.com | Sends you to https://independentclaimsconsultants.com |
| https://independentclaimsconsultants.com/loss-assessors-surrey/ | Southern office page |
| https://independentclaimsconsultants.com/contact-2/ | Sends you to /contact/ |
| https://independentclaimsconsultants.com/sample-page/ | Sends you to the homepage |
| https://independentclaimsconsultants.com/anything-made-up/ | The "page not found" page |

## Step 6: Switch on the enquiry form (one time only)

The claim form sends through FormSubmit, a free service. Enquiries go to andy@independentclaimsconsultants.com, with a copy to nic@independentclaimsconsultants.co.uk.

1. Go to https://independentclaimsconsultants.com/contact/ and send a test enquiry with your own details.
2. Andy will receive an email from FormSubmit asking to **activate** the form. Click the button in that email. Check the spam folder if it doesn't arrive.
3. Send a second test enquiry. This one should arrive in both inboxes.

Until the activation link is clicked, enquiries aren't delivered, so do this straight after going live.

**Optional:** after activation, FormSubmit emails a random code that can replace Andy's address in the form. This hides Andy's address from spam bots. To use it, change `FORM_ENDPOINT` in `_build/build.py` to `https://formsubmit.co/` followed by the code, rebuild and re-upload.

## If something goes wrong

To switch back to WordPress:

1. Move the new files into a new folder, such as `new-site`.
2. Move everything in `old-wordpress` back into the website folder.

## Straight after going live

- **Google Search Console:** add the domain, then submit `https://independentclaimsconsultants.com/sitemap.xml`. Use **URL Inspection** to request indexing of the homepage and the Surrey page.
- **Bing Webmaster Tools:** import the site from Search Console.
- **Later:** once you're happy, after a month or so, you can delete `old-wordpress`. You can also delete the WordPress database in cPanel under **MySQL Databases**.

## Updating the site later

1. Make the change in `_build`.
2. Run `python3 _build/package.py`.
3. Upload and extract the new zip over the old files, choosing to overwrite.
