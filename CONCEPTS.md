# Concepts: S3 + CloudFront Secure Static Site

## 1. Why S3 for Static Hosting?
S3 (Simple Storage Service) is object storage — it stores files (HTML, CSS, JS, images).
For static sites, S3 is ideal because:
- No server to manage or patch
- Infinitely scalable
- Pay only for what you store and serve
- Highly durable (99.999999999% — 11 nines)

## 2. Why NOT enable S3 Static Website Hosting?
S3 has a built-in "static website hosting" feature — but we deliberately keep it OFF.
Reason: S3 website endpoints only support HTTP, not HTTPS.
Instead, we serve via CloudFront which handles HTTPS for us.
Direct S3 URL access is also blocked — users can only reach the site via CloudFront.

## 3. What is CloudFront?
CloudFront is AWS's CDN (Content Delivery Network).
It caches your content at edge locations around the world (400+ globally).
Benefits:
- HTTPS support with free SSL certificate
- Faster load times (content served from nearest edge location)
- DDoS protection built-in (AWS Shield Standard — free)
- Hides your S3 bucket from direct public access

## 4. What is OAC (Origin Access Control)?
OAC is a CloudFront feature that signs every request sent from CloudFront to S3.
S3 bucket policy only allows requests that come with this signature.

Result:
- Direct S3 URL → 403 Forbidden
- Via CloudFront URL → 200 OK

OAC replaced the older OAI (Origin Access Identity) because:
- OAC supports AWS Signature Version 4 (more secure)
- OAC works with SSE-KMS encrypted buckets
- OAI is now legacy

In the newer CloudFront console wizard, OAC is set up automatically when you check "Allow private S3 bucket access to CloudFront" during origin creation — CloudFront creates the OAC and, after distribution creation, offers to write the matching bucket policy for you (see screenshot 01).

## 5. What is a Bucket Policy?
A JSON document attached to an S3 bucket that defines who can access it and how.
Our bucket policy:
- Allows only CloudFront service principal (cloudfront.amazonaws.com)
- Only for the specific CloudFront distribution (via SourceArn condition)
- Only allows s3:GetObject (read only — no write, no delete)

## 6. Block Public Access
All 4 Block Public Access settings are enabled on our bucket.
This means:
- No ACLs can make objects public
- No bucket policy can make objects public
- Even if someone accidentally writes a permissive policy, AWS blocks it

## 7. Encryption at Rest (SSE-S3)
All objects stored in S3 are encrypted using AWS-managed keys (SSE-S3).
- Encryption happens automatically on upload
- Decryption happens automatically on download
- No cost beyond storage
- SSE-KMS is an alternative with customer-managed keys (costs extra per API call)

## 8. Versioning
S3 versioning keeps all versions of every object.
If index.html is overwritten accidentally, you can restore the previous version.
Useful for: rollback, audit trail, accidental deletion recovery.

## 9. Server Access Logging
S3 and CloudFront can each log every request independently:
- **S3 server access logging** — logs requests made directly to the bucket (requester IP, timestamp, operation, response code)
- **CloudFront standard logging** — logs requests at the edge, before they even reach S3 (viewer IP, requested object, edge location, cache hit/miss)

Both are configured to write to the same logs bucket (`palakpreet-s3-cloudfront-logs`), giving visibility at both layers. Use case: security auditing, debugging, compliance.

## 10. HTTPS Only (Viewer Protocol Policy)
CloudFront's default cache behavior is set to "Redirect HTTP to HTTPS."
This ensures all traffic is encrypted in transit (TLS) — a visitor typing `http://` is automatically bounced to `https://` rather than served an error.
No user can accidentally access the site unencrypted.

## 11. Custom Error Responses
By default, a 403 from S3 (via CloudFront) returns raw XML — not user-friendly and reveals backend details.
A custom error response is configured on the distribution: HTTP 403 → serve `/error.html` instead.
This keeps the error experience consistent with the rest of the site and avoids exposing internal error structure to visitors.

## 12. Cache Policy
Rather than leaving cache behavior on unconfigured defaults, the distribution uses AWS's **recommended cache policy for S3 content** (CachingOptimized), selected during origin setup. This is a deliberate choice, not an accident:
- Tuned for static content that doesn't change per-request (no cookies/headers needed in the cache key)
- Reduces origin requests to S3, lowering cost and latency
- A custom policy would only be needed if the site later required per-user personalization or query-string-based caching

## 13. Why I Skipped WAF
AWS WAF adds protection against SQL injection, XSS, and bad bots, but costs roughly $14+/month for a web ACL plus per-request charges. For a personal portfolio project with no sensitive backend, no user input, and no login flow, the attack surface WAF protects against doesn't really apply yet. Documented here as a conscious cost/tradeoff decision, not an oversight — and listed under "What I Would Add in Production" since a real production app serving user input would need it.

## 14. Why I Chose These Services
| Requirement | Service Used | Reason |
|---|---|---|
| Store static files | S3 | Cheap, durable, serverless |
| HTTPS + CDN | CloudFront | Free SSL, global edge caching |
| Secure origin access | OAC | Signs requests, blocks direct S3 access |
| Encryption at rest | SSE-S3 | Free, automatic, sufficient for portfolio |
| Access logging | S3 + CloudFront logging | Audit trail, security visibility at both layers |

## 15. Verifying the Security Model
Two tests prove the setup works as designed, rather than just assuming it does:
1. **CloudFront URL loads correctly** — proves the happy path works (screenshot 08)
2. **Direct S3 URL returns `AccessDenied`** — proves the bucket is genuinely private and CloudFront/OAC is the only valid path in (screenshot 09)

Testing both the allowed and denied paths is what makes this a security claim you can demonstrate, not just one you assert.

## 16. What I Would Add in Production
- AWS WAF (Web Application Firewall) — block SQLi, XSS, bad bots ($14/month)
- Custom domain via Route 53 + ACM certificate
- SSE-KMS instead of SSE-S3 for stricter key control
- S3 Object Lock for compliance use cases
