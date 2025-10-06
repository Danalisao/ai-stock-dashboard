# 📧 Gmail App Password - Guide Rapide

## Erreur: "Application-specific password required"

Vous voyez cette erreur car Gmail nécessite un **App Password** spécial (pas votre mot de passe normal).

---

## Solution en 3 Étapes (2 minutes)

### 1️⃣ Activer la Validation en 2 Étapes

1. Allez sur: **https://myaccount.google.com/security**
2. Cliquez sur **"Validation en 2 étapes"** (ou "2-Step Verification")
3. Suivez les instructions pour l'activer (avec votre téléphone)

⚠️ **IMPORTANT**: Sans 2FA activée, vous ne pourrez PAS créer d'App Password !

---

### 2️⃣ Générer un App Password

Une fois 2FA activée :

1. Allez sur: **https://myaccount.google.com/apppasswords**
2. Connectez-vous si nécessaire
3. Dans "Select app", choisissez **"Mail"** ou **"Other"**
4. Dans "Select device", choisissez **"Windows Computer"** ou entrez "Stock Dashboard"
5. Cliquez **"Generate"**

Vous obtiendrez un code à **16 caractères** comme:
```
abcd efgh ijkl mnop
```

**⚠️ COPIEZ-LE IMMÉDIATEMENT** - Vous ne pourrez plus le voir après !

---

### 3️⃣ Ajouter dans .env

Ouvrez votre fichier `.env` et ajoutez (SANS espaces) :

```env
# Gmail Configuration
GMAIL_EMAIL=votre.email@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop
```

**Notes importantes:**
- ❌ PAS d'espaces dans le mot de passe : `abcdefghijklmnop`
- ✅ Pas besoin de guillemets
- ✅ Tout en minuscules (ou majuscules, peu importe)

---

## Exemple Complet .env

```env
# Telegram
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789

# Gmail (App Password - PAS votre mot de passe normal!)
GMAIL_EMAIL=john.doe@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop

# Gemini AI
GEMINI_API_KEY=AIzaSyC...your_key_here
```

---

## Tester

```bash
python test_alerts.py
```

Vous devriez maintenant recevoir :
- ✅ Email dans votre boîte Gmail
- ✅ Telegram sur votre téléphone
- ✅ Desktop notification sur Windows

---

## Liens Rapides

- **2FA:** https://myaccount.google.com/security
- **App Passwords:** https://myaccount.google.com/apppasswords
- **Support Google:** https://support.google.com/accounts/answer/185833

---

## Troubleshooting

### "Cette page n'est pas disponible"

➡️ Vous n'avez probablement pas activé la 2FA. Allez d'abord sur:
https://myaccount.google.com/security

### "Mot de passe incorrect"

- ✅ Vérifiez qu'il n'y a PAS d'espaces dans le .env
- ✅ Régénérez un nouveau App Password
- ✅ Utilisez l'App Password (16 caractères), PAS votre mot de passe Gmail

### Email fonctionne mais pas Telegram

➡️ Problème différent - voir `ALERT_SETUP_GUIDE.md` section Telegram

---

## Sécurité 🔐

### Bonnes Pratiques

✅ **Générez un App Password par application**
- Un pour Stock Dashboard
- Un pour mobile email client
- etc.

✅ **Révoquez les anciens si compromis**
- https://myaccount.google.com/apppasswords
- Cliquez sur la poubelle à côté du mot de passe

✅ **Ne partagez JAMAIS votre App Password**
- Gardez le `.env` privé
- Ne le commitez pas sur GitHub

---

**Après configuration, les alertes email seront envoyées automatiquement !** 📧✅
