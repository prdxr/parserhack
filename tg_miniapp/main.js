import { Telegraf, Markup } from "telegraf";
import { message } from "telegraf/filters";
import "dotenv/config";

const token = process.env.TOKEN;
const webapp_url = process.env.WEB_APP_URL;

const bot = new Telegraf(token);

bot.command("start", (ctx) => {
    ctx.reply(
        "Добро пожаловать! Нажмите на кнопку ниже, чтобы войти в приложение.",
        Markup.keyboard([
            Markup.button.webApp("Войти в Event Voyager", `${webapp_url}`),
        ]).resize()
    )
});

bot.launch();