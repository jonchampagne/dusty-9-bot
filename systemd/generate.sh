
bot_service="dusty-9-bot"

wd=`dirname $0`

root_dir=`realpath "$wd"/..`

bot_template="
[Unit]
Description=Dusty 9 Bot
After=network.target

[Service]
User=jon
Restart=always
Type=simple
WorkingDirectory=$root_dir
ExecStart=$root_dir/run.sh

[Install]
WantedBy=multi-user.target
"

watcher_template="
[Unit]
Description=Dusty 9 Bot Restarter
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/bin/systemctl restart $bot_service.service

[Install]
WantedBy=multi-user.target
"

path_template="
[Path]
PathModified=$root_dir

[Install]
WantedBy=multi-user.target
"

update_template="
[Unit]
Description=Update Dusty 9 Bot
After=network.target

[Service]
Type=oneshot
WorkingDirectory=$root_dir
ExecStart=/usr/bin/git pull
"

update_timer_template="
[Unit]
Description=Update Dusty 9 Bot

[Timer]
OnCalendar=* *-*-* *:00:00

[Install]
WantedBy=timers.target
"

echo "$bot_template" > "$bot_service".service
echo "Generated $bot_service.service"

echo "$watcher_template" > "$bot_service"-watcher.service
echo "Generated $bot_service-watcher.service"

echo "$path_template" > "$bot_service".path
echo "Generated $bot_service.path"

echo "$update_template" > update-"$bot_service".service
echo "Generated update-$bot_service.service"

echo "$update_timer_template" > update-"$bot_service".timer
echo "Generated update-$bot_service.timer"

