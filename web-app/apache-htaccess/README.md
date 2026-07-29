# Apache And Htaccess Review

Apache-based applications often hide important behavior in `.htaccess` files, vhost config, rewrite rules, handler mappings, and directory-level overrides. These controls can decide whether files are executable, browsable, protected, redirected, cached, or treated as source.

## What To Check

Look for Apache-specific signals:

* `Server: Apache` response headers.
* `X-Powered-By: PHP` with Apache-style routing.
* WordPress, Laravel, CodeIgniter, cPanel, WHM, shared hosting, or classic LAMP patterns.
* URLs shaped by rewrite rules, such as extensionless PHP routes.
* Public upload directories under the same web root as executable code.

## Htaccess Exposure

`.htaccess` itself should not be downloadable. Also check common backup and editor variants:

```text
/.htaccess
/.htaccess.bak
/.htaccess.old
/.htaccess.save
/.htaccess~
/backup/.htaccess
/uploads/.htaccess
```

If exposed, it can reveal:

* Protected admin paths.
* Basic auth file locations.
* Rewrite rules and hidden routes.
* Environment variables.
* PHP handler behavior.
* Upload restrictions.
* Legacy migration paths.

Developer fix:

* Deny access to dotfiles.
* Keep backups outside the web root.
* Disable directory listing.
* Move sensitive rules into vhost config where possible.

## Override And Directory Scope

Apache can apply different rules per directory. A secure root config can be weakened by a nested `.htaccess` in `uploads`, `assets`, `storage`, or legacy folders.

Review:

* Is `AllowOverride` enabled too broadly?
* Can app deployments write `.htaccess` into public directories?
* Do nested rules re-enable script execution?
* Are upload directories configured as static-only?
* Are old app folders still reachable with different rules?

Developer fix:

* Use `AllowOverride None` where possible.
* Permit overrides only where needed.
* Make upload/storage directories non-executable.
* Keep deployment users from writing server control files into public paths.

## Directory Listing

Apache directory listing can expose source, backups, logs, exports, and uploaded files.

Check for:

* `Options Indexes` enabled.
* Browsable `/uploads/`, `/backup/`, `/old/`, `/storage/`, `/logs/`, `/vendor/`, or `/admin/`.
* File names that reveal internal routes, users, tenants, invoices, or exports.

Developer fix:

* Disable `Options Indexes`.
* Add index denial for storage directories.
* Store private files outside the document root.

## Rewrite Rule Mistakes

Rewrite rules often become authorization logic by accident.

Common issues:

* Admin paths hidden by redirects but still directly callable.
* API routes reachable through alternate paths.
* Case-sensitive or encoded path bypasses.
* Old routes preserved for migration but not protected.
* Rules that protect UI pages but not backend endpoints.
* Rewrite conditions that trust `Host`, `X-Forwarded-*`, or user-controlled path fragments.

Developer fix:

* Enforce authorization in application code and backend policy, not only rewrite rules.
* Normalize paths before authorization.
* Remove legacy routes after migration.
* Test protected endpoints through alternate encodings, casing, and direct paths.

## Basic Auth And Access Files

Apache Basic Auth is often used to protect admin panels, staging copies, dashboards, and temporary tools.

Review:

* Is `.htpasswd` inside the web root?
* Are backup copies of `.htpasswd` exposed?
* Are protected directories also reachable through rewritten routes?
* Is Basic Auth missing on API paths used by the protected UI?
* Are weak shared credentials used across staging and production?

Developer fix:

* Store password files outside the web root.
* Protect both UI and backing API endpoints.
* Use strong unique credentials or SSO.
* Remove temporary Basic Auth rules after migration.

## PHP Handler And Upload Risks

Apache plus PHP can become dangerous when upload directories execute scripts.

Check:

* Can uploaded files run as PHP, PHP5, PHTML, PHAR, or other handler-mapped extensions?
* Do `.htaccess` rules in upload directories change handlers?
* Are MIME type checks used instead of extension and content validation?
* Are image transformations storing originals in executable paths?
* Are old Apache/PHP handler mappings still active?

Developer fix:

* Disable script execution in upload and storage directories.
* Store uploads outside the web root or serve them through a controlled download endpoint.
* Allowlist extensions and verify content.
* Remove legacy PHP handler mappings.

## Sensitive File Exposure

Apache web roots commonly leak project files when deployment paths are sloppy.

Check for:

```text
/.env
/composer.json
/composer.lock
/vendor/
/storage/logs/
/error_log
/phpinfo.php
/server-status
/server-info
/backup.zip
/site.tar.gz
```

Developer fix:

* Keep secrets and build artifacts outside the document root.
* Disable `server-status` and `server-info` publicly.
* Block common backup/archive extensions.
* Clean old deployments and temporary files.

Use only on systems where you have authorization to test.
