# Scripts to check data integrity beyond built-in checks and constraints.

# Ensure that each authority at most one primary document.
SELECT authority.authorityId, COUNT(authority.authorityId) as CNT
FROM authority
LEFT JOIN authorityDocument ON authority.authorityId = authorityDocument.authorityId
WHERE authorityDocument.primary = 1
GROUP BY authority.authorityId
HAVING CNT > 1;

# Ensure that each authority has at least one document.
SELECT authority.authorityId
FROM authority
LEFT JOIN authorityDocument ON authority.authorityId = authorityDocument.authorityId
WHERE authorityDocument.authorityDocumentId IS NULL
GROUP BY authority.authorityId;
