const TelegramBot = require('node-telegram-bot-api');
const fs = require('fs');

const TOKEN = process.env.TELEGRAMBOTTOKEN;
const ADMINID = Number(process.env.ADMINID);

if (!TOKEN || !ADMINID) {
  throw new Error('Не заданы TELEGRAMBOTTOKEN или ADMINID в переменных окружения');
}

const SETTINGSFILE = './settings.json';

function loadSettings() {
  try {
    const data = fs.readFileSync(SETTINGSFILE, 'utf-8');
    return JSON.parse(data);
  } catch {
    return { chatId: null, message: null, schedule: null };
  }
}

function saveSettings(settings) {
  fs.writeFileSync(SETTINGSFILE, JSON.stringify(settings, null, 2));
}

const bot = new TelegramBot(TOKEN, { webHook: true });

let settings = loadSettings();

function isAdmin(id) {
  return id === ADMINID;
}

function checkSchedule() {
  if (!settings.schedule || !settings.chatId || !settings.message) return;

  const now = new Date();
  const utcHour = now.getUTCHours();
  const utcMinute = now.getUTCMinutes();

  if (settings.schedule.hour === utcHour && settings.schedule.minute === utcMinute) {
    bot.sendMessage(settings.chatId, settings.message).catch(console.error);
  }
}

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    res.status(405).send('Method Not Allowed');
    return;
  }

  try {
    const update = req.body;
    bot.processUpdate(update);

    if (update.message) {
      const msg = update.message;
      if (!isAdmin(msg.from.id)) {
        await bot.sendMessage(msg.chat.id, 'У вас нет доступа.');
        res.status(200).send('OK');
        return;
      }

      const text = msg.text;

      switch (text) {
        case '/start':
          await bot.sendMessage(msg.chat.id, 'Вы админ. Что хотите сделать?', {
            replymarkup: {
              keyboard: [
                ['Установить канал/группу'],
                ['Установить сообщение'],
                ['Запланировать пост'],
                ['Отменить расписание'],
              ],
              resizekeyboard: true,
              onetimekeyboard: true,
            },
          });
          break;

        case 'Установить канал/группу':
          await bot.sendMessage(msg.chat.id, 'Отправьте ID канала/группы (например, @channelname или числовой ID)');
          fs.writeFileSync('state.json', JSON.stringify({ chatId: msg.chat.id, action: 'setChatId' }));
          break;

        case 'Установить сообщение':
          await bot.sendMessage(msg.chat.id, 'Отправьте текст сообщения для публикации');
          fs.writeFileSync('state.json', JSON.stringify({ chatId: msg.chat.id, action: 'setMessage' }));
          break;

        case 'Запланировать пост':
          await bot.sendMessage(msg.chat.id, 'Отправьте время в формате ЧЧ:ММ (например, 14:30)');
          fs.writeFileSync('state.json', JSON.stringify({ chatId: msg.chat.id, action: 'setSchedule' }));
          break;

        case 'Отменить расписание':
          settings.schedule = null;
          saveSettings(settings);
          await bot.sendMessage(msg.chat.id, 'Расписание отменено.');
          break;

        default:
          let state = null;
          try {
            state = JSON.parse(fs.readFileSync('state.json', 'utf-8'));
          } catch {}
          if (state && state.chatId === msg.chat.id) {
            if (state.action === 'setChatId') {
              settings.chatId = text.trim();
              saveSettings(settings);
              await bot.sendMessage(msg.chat.id, Канал/группа установлены: ${settings.chatId});
              fs.unlinkSync('state.json');
            } else if (state.action === 'setMessage') {
              settings.message = text;
              saveSettings(settings);
              await bot.sendMessage(msg.chat.id, 'Сообщение сохранено.');
              fs.unlinkSync('state.json');
            } else if (state.action === 'setSchedule') {
              const time = text.trim();
              const match = time.match(/^(\d{1,2}):(\d{2})$/);
              if (!match) {await bot.sendMessage(msg.chat.id, 'Неверный формат времени. Попробуйте снова.');
              } else {
                const hour = Number(match1);
                const minute = Number(match2);
                if (hour > 23 || minute > 59) {
                  await bot.sendMessage(msg.chat.id, 'Неверное время. Попробуйте снова.');
                } else if (!settings.chatId || !settings.message) {
                  await bot.sendMessage(msg.chat.id, 'Сначала установите канал/группу и сообщение.');
                } else {
                  settings.schedule = { hour, minute };
                  saveSettings(settings);
                  await bot.sendMessage(msg.chat.id, Расписание установлено на ${time} (UTC).);
                }
              }
              fs.unlinkSync('state.json');
            } else {
              await bot.sendMessage(msg.chat.id, 'Неизвестное действие.');
              fs.unlinkSync('state.json');
            }
          }
          break;
      }
    }

    checkSchedule();

    res.status(200).send('OK');
  } catch (error) {
    console.error(error);
    res.status(500).send('Internal Server Error');
  }
};
