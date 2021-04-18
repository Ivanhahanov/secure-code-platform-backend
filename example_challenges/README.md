# Upload Challenges
## Challenges file struct 
```bash
challenges/
  description.yml
  files/
```
## Description format
Example: `description.yml`
```yaml
shortname:
  title: "Full challenge name",
  text: "Task description",
  score: 10,
  tags: 
    - sql
    - boolean-based
  category: web,
  difficulty_tag: easy,
  port: 8080
  useful_resources:
    - https://owasp.org/www-community/attacks/SQL_Injection
```
