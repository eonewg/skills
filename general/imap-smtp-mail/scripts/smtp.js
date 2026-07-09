#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const os = require('os');
const dotenv = require('dotenv');
const nodemailer = require('nodemailer');

function expandHome(p){ return p && p.startsWith('~') ? path.join(os.homedir(), p.slice(1)) : p; }
const envFile = process.env.EMAIL_ENV_FILE || path.join(os.homedir(), '.openclaw/credentials/imap-smtp-mail.env');
if (fs.existsSync(envFile)) dotenv.config({ path: envFile });

function parseArgs(argv){
  const args = { _: [] };
  for(let i=0;i<argv.length;i++){
    const a=argv[i];
    if(a.startsWith('--')){
      const k=a.slice(2);
      if(['approve','debug'].includes(k)) args[k]=true;
      else args[k]=argv[++i];
    } else args._.push(a);
  }
  return args;
}
function allowed(file, envName){
  const val = process.env[envName] || '';
  const dirs = val.split(',').map(s=>expandHome(s.trim())).filter(Boolean).map(d=>path.resolve(d));
  const rp = path.resolve(expandHome(file));
  return dirs.length === 0 || dirs.some(d => rp === d || rp.startsWith(d + path.sep));
}
function readAllowed(file){
  if(!allowed(file, 'ALLOWED_READ_DIRS')) throw new Error(`Path not allowed by ALLOWED_READ_DIRS: ${file}`);
  return fs.readFileSync(expandHome(file), 'utf8');
}
function simpleHtml(text){
  return text.split(/\n\n+/).map(p=>`<p>${p.replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])).replace(/\n/g,'<br>')}</p>`).join('\n');
}
async function saveToSent(raw){
  if(process.env.IMAP_SAVE_SENT === 'false' || !process.env.IMAP_HOST || !process.env.IMAP_USER || !process.env.IMAP_PASS) return {savedToSent:false};
  const { ImapFlow } = require('imapflow');
  const client = new ImapFlow({
    host: process.env.IMAP_HOST,
    port: Number(process.env.IMAP_PORT || 993),
    secure: String(process.env.IMAP_TLS || 'true') !== 'false',
    auth: { user: process.env.IMAP_USER, pass: process.env.IMAP_PASS },
    tls: { rejectUnauthorized: String(process.env.IMAP_REJECT_UNAUTHORIZED || 'true') !== 'false' },
    logger: false
  });
  await client.connect();
  let mailbox = process.env.IMAP_SENT_MAILBOX;
  if(!mailbox){
    const boxes = await client.list();
    const sent = boxes.find(b => Array.from(b.flags || []).includes('\\Sent')) || boxes.find(b => /sent|已发送|寄件|发件/i.test(b.path));
    mailbox = sent ? sent.path : 'Sent';
  }
  try { await client.append(mailbox, Buffer.from(raw), ['\\Seen'], new Date()); await client.logout(); return {savedToSent:true, sentMailbox:mailbox}; }
  catch(e){ try{ await client.logout(); }catch{} return {savedToSent:false, sentMailbox:mailbox, sentCopyError:e.message}; }
}
async function main(){
  const [cmd] = process.argv.slice(2);
  if(cmd === 'contacts'){ console.log(JSON.stringify({contacts:[]}, null, 2)); return; }
  if(cmd === 'test'){
    process.argv.push('--to', process.env.SMTP_USER || process.env.SMTP_FROM, '--subject', 'SMTP test', '--body', 'SMTP test', '--approve');
  }
  if(cmd !== 'send' && cmd !== 'test') throw new Error('Usage: smtp.js send ...');
  const args = parseArgs(process.argv.slice(3));
  const to = args.to;
  const subject = args.subject || (args['subject-file'] ? readAllowed(args['subject-file']).trim() : '');
  const text = args['body-file'] ? readAllowed(args['body-file']) : (args.body || '');
  const html = args['html-file'] ? readAllowed(args['html-file']) : (args.html || simpleHtml(text));
  const draft = { to, subject, text, html };
  if(!args.approve){ console.log(JSON.stringify({approvalRequired:true, draft}, null, 2)); return; }
  const transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST,
    port: Number(process.env.SMTP_PORT || 587),
    secure: String(process.env.SMTP_SECURE || 'false') === 'true',
    auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS },
    name: process.env.SMTP_CLIENT_NAME || undefined,
    tls: { rejectUnauthorized: String(process.env.SMTP_REJECT_UNAUTHORIZED || 'true') !== 'false' },
    debug: !!args.debug,
    logger: !!args.debug
  });
  const fromAddr = process.env.SMTP_FROM || process.env.SMTP_USER;
  const fromName = process.env.SMTP_FROM_NAME;
  const mail = { from: fromName ? `"${fromName.replace(/"/g,'\\"')}" <${fromAddr}>` : fromAddr, to, subject, text, html, replyTo: process.env.SMTP_REPLY_TO || undefined };
  const info = await transporter.sendMail(mail);
  let raw = '';
  try {
    const builder = nodemailer.createTransport({ streamTransport: true, buffer: true, newline: 'unix' });
    const built = await builder.sendMail(mail);
    raw = Buffer.isBuffer(built.message) ? built.message.toString() : String(built.message || '');
  } catch {}
  let sent = raw ? await saveToSent(raw) : {savedToSent:false, sentCopyError:'raw message unavailable'};
  console.log(JSON.stringify({sent:true, messageId: info.messageId, response: info.response, envelope: info.envelope, accepted: info.accepted, rejected: info.rejected, ...sent}, null, 2));
}
main().catch(e=>{ console.error(e && e.stack || e); process.exit(1); });
