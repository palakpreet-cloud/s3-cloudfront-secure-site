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
- Direct S3 URL →  403 Forbidden
- Via CloudFront URL →  200 OK

OAC replaced the older OAI (Origin Access Identity) because:
- OAC supports AWS Signature Version 4 (more secure)
- OAC works with SSE-KMS encrypted buckets
- OAI is now legacy

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
S3 logs every request made to the bucket into a separate logs bucket.
Logs include: requester IP, timestamp, operation, response code.
Use case: security auditing, debugging, compliance.

## 10. HTTPS Only (Viewer Protocol Policy)
CloudFront is configured to redirect HTTP → HTTPS.
This ensures all traffic is encrypted in transit (TLS).
No user can accidentally access the site over plain HTTP.

## 11. Why I Chose These Services
| Requirement | Service Used | Reason |
|---|---|---|
| Store static files | S3 | Cheap, durable, serverless |
| HTTPS + CDN | CloudFront | Free SSL, global edge caching |
| Secure origin access | OAC | Signs requests, blocks direct S3 access |
| Encryption at rest | SSE-S3 | Free, automatic, sufficient for portfolio |
| Access logging | S3 Server Access Logging | Audit trail, security visibility |

## 12. What I Would Add in Production
- AWS WAF (Web Application Firewall) — block SQLi, XSS, bad bots ($14/month)
- Custom domain via Route 53 + ACM certificate
- SSE-KMS instead of SSE-S3 for stricter key control
- CloudFront access logs (separate from S3 access logs)
- S3 Object Lock for compliance use cases
