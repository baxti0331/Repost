
const TelegramBot = require('node-telegram-bot-api');
const schedule = require('node-schedule');
const fs = require('fs');

const TOKEN = 7654397697:AAFQcNyz--NU_l3PJ_VQVYkUwgh7T_k1Yec;// Вставьте сюда ваш токен
const ADMIN_ID = 7794270699; // Вставьте сюда ваш админ ID числом

const SETTINGS_FILE = './settings.json';

function loadSettings() {
  try {
    const data = fs.readFileSync(SETTINGS_FILE, 'utf-8');
    return JSON.parse(data);
  } catch {
    return { chatId: null, message: null };
  }
}

function saveSettings(settings) {
  fs.writeFileSync(SETTINGS_FILE, JSON.stringify(settings, null, 2));
}

const bot = new TelegramBot(TOKEN, { polling: true });

let settings = loadSettings();
let job = null;

function isAdmin(id) {
  return id === ADMIN_ID;
}

function scheduleJob(hour, minute) {
  if (job) job.cancel();

  const rule = new schedule.RecurrenceRule();
  rule.hour = hour;
  rule.minute = minute;
  rule.tz = 'Etc/UTC';

  job = schedule.scheduleJob(rule, () => {
    if (settings.chatId && settings.message) {
      bot.sendMessage(settings.chatId, settings.message).catch(console.error);
    }
  });
}

bot.onText(/\/start/, (msg) => {
  if (!isAdmin(msg.from.id)) {
    bot.sendMessage(msg.chat.id, 'У вас нет доступа.');
    return;
  }
  bot.sendMessage(msg.chat.id, 'Вы админ. Что хотите сделать?', {
    reply_markup: {
      keyboard: [
        ['Установить канал/группу'],
        ['Установить сообщение'],
        ['Запланировать пост'],
        ['Отменить расписание'],
      ],
      resize_keyboard: true,
      one_time_keyboard: true,
    },
  });
});

bot.on('message', (msg) => {
  if (!isAdmin(msg.from.id)) return;

  const text = msg.text;

  switch (text) {
    case 'Установить канал/группу':
      bot.sendMessage(msg.chat.id, 'Отправьте ID канала/группы (например, @channelname или числовой ID)');
      bot.once('message', (answer) => {
        settings.chatId = answer.text.trim();
        saveSettings(settings);
        bot.sendMessage(msg.chat.id, `Канал/группа установлены: ${settings.chatId}`);
      });
      break;

    case 'Установить сообщение':
      bot.sendMessage(msg.chat.id, 'Отправьте текст сообщения для публикации');
      bot.once('message', (answer) => {
        settings.message = answer.text;
        saveSettings(settings);
        bot.sendMessage(msg.chat.id, 'Сообщение сохранено.');
      });
      break;

    case 'Запланировать пост':
      bot.sendMessage(msg.chat.id, 'Отправьте время в формате ЧЧ:ММ (например, 14:30)');
      bot.once('message', (answer) => {
        const time = answer.text.trim();
        const match = time.match(/^(\d{1,2}):(\d{2})$/);
        if (!match) {
          bot.sendMessage(msg.chat.id, 'Неверный формат времени. Попробуйте снова.');
          return;
        }
        const hour = Number(match[1]);
        const minute = Number(match[2]);
        if (hour > 23 || minute > 59) {
          bot.sendMessage(msg.chat.id, 'Неверное время. Попробуйте снова.');
          return;
        }

        if (!settings.chatId || !settings.message) {
          bot.sendMessage(msg.chat.id, 'Сначала установите канал/группу и сообщение.');
          return;
        }

        scheduleJob(hour, minute);
        bot.sendMessage(msg.chat.id, `Расписание установлено на ${time} (UTC).`);
      });
      break;

    case 'Отменить расписание':
      if (job) {
        job.cancel();
        job = null;
        bot.sendMessage(msg.chat.id, 'Расписание отменено.');
      } else {
        bot.sendMessage(msg.chat.id, 'Нет активного расписания.');
      }
      break;
  }
});
