from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters
from telegram.request import HTTPXRequest
import logging
import config
import handlers

# فعال‌سازی لاگ برای دیدن خطاهای احتمالی شبکه
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

if __name__ == '__main__':
    print("🚀 Bale Bot Starting...")
    
    # --- تغییر مهم: تنظیم دقیق تایم‌اوت‌ها برای بله ---
    # سرورهای بله گاهی در اتصالات طولانی پاسخ نمی‌دهند.
    # ما تایم‌اوت را کم می‌کنیم تا اگر پاسخی نیامد، سریع دوباره درخواست دهد.
    request_settings = HTTPXRequest(
        connection_pool_size=10,
        read_timeout=10.0,    # زمان انتظار برای خواندن پاسخ (کم شده)
        write_timeout=10.0,   # زمان انتظار برای ارسال
        connect_timeout=10.0, # زمان انتظار برای اتصال اولیه
        media_write_timeout=20.0,
    )

    app = ApplicationBuilder() \
        .token(config.BALE_TOKEN) \
        .base_url(config.BALE_API_BASE_URL) \
        .base_file_url(config.BALE_FILE_BASE_URL) \
        .request(request_settings) \
        .get_updates_request(request_settings) \
        .build()
    
    # هندلر لینک هوشمند
    deep_link = MessageHandler(filters.Regex(r"/info"), handlers.deep_link_handler)

    conv = ConversationHandler(
        entry_points=[
            CommandHandler('start', handlers.start),
            deep_link,
            # این خط برای منوی اصلی است
            MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.menu_router)
        ],
        states={
            config.MENU_STATE: [
                deep_link,
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.menu_router),
                CallbackQueryHandler(handlers.callback_handler)
            ],
            # --- لیست‌گیری ---
            config.WAIT_LIST_FILTER: [MessageHandler(filters.TEXT, handlers.list_filter)],
            config.WAIT_LIST_PARENT: [MessageHandler(filters.TEXT, handlers.list_parent)],
            config.WAIT_LIST_SUB: [MessageHandler(filters.TEXT, handlers.list_sub)],
            
            # --- تغییر قیمت گروهی ---
            config.WAIT_BULK_SCOPE: [MessageHandler(filters.TEXT, handlers.bulk_scope)],
            config.WAIT_BULK_CAT: [MessageHandler(filters.TEXT, handlers.bulk_cat)],
            config.WAIT_BULK_METHOD: [MessageHandler(filters.TEXT, handlers.bulk_method)],
            config.WAIT_BULK_VALUE: [MessageHandler(filters.TEXT, handlers.bulk_value)],
            config.WAIT_BULK_CONFIRM: [MessageHandler(filters.TEXT, handlers.bulk_confirm)],
            
            # --- حذف قیمت گروهی (جایی که گیر کرده بودید) ---
            config.WAIT_REM_SCOPE: [MessageHandler(filters.TEXT, handlers.remove_scope)],
            config.WAIT_REM_CAT: [MessageHandler(filters.TEXT, handlers.remove_cat)],
            config.WAIT_REM_CONFIRM: [MessageHandler(filters.TEXT, handlers.remove_confirm)],
            
            # --- ورودی‌های تکی ---
            config.WAIT_INPUT_PRICE: [MessageHandler(filters.TEXT, handlers.input_price)],
            config.WAIT_INPUT_ADD: [MessageHandler(filters.TEXT, handlers.input_add_stock)],
            config.WAIT_INPUT_REDUCE: [MessageHandler(filters.TEXT, handlers.input_reduce_stock)],
            
            # --- خروجی اکسل ---
            config.WAIT_EXP_TYPE: [MessageHandler(filters.TEXT, handlers.export_type)],
            config.WAIT_EXP_SCOPE: [MessageHandler(filters.TEXT, handlers.export_scope_handler)],
            config.WAIT_EXP_CAT: [MessageHandler(filters.TEXT, handlers.export_cat_handler)],
        },
        # دستور انصراف سراسری
        fallbacks=[
            CommandHandler('cancel', handlers.cancel),
            MessageHandler(filters.Regex("^انصراف$"), handlers.cancel)
        ]
    )
    
    app.add_handler(conv)
    
    print("✅ Bot is running. Waiting for messages...")
    
    # --- تغییر مهم در Polling ---
    # poll_interval: هر چند ثانیه سرور را چک کند (کمتر = سریعتر)
    # timeout: چقدر منتظر بماند تا سرور بله پاسخ دهد (باید با read_timeout هماهنگ باشد)
    app.run_polling(poll_interval=1.0, timeout=10)