# Original FML
### How to run
1. Change the `conf/conf.yml` to your preference.
2. Feel free to use `open_terminals.sh` or `open_tmux.sh`. Each assumes you are using GNOME and/or tmux repectively. By default, they open three windows or three panels.
3. Run `src/server.py`, `src/client1.py`, and `src/client2.py`. If you want more number of parties, change the configuration and create `src/clientN.py` by copying (after that change the `client_name` variable value.)
4. After all socket connections get established, the server creates an initial model. Send any message from client side. Server returns the location of init-model. Once the clients receive it, they start updating the init-model using their own data (`n` in `conf/conf.yml` is for the number of samples to train). After they finish each training, they report the server about the locations of the updated models. This Round will continue for `rounds` (you define) times.


## Important!
On the client side, do not interrupt the update on the server side. After sending the locally updated model to the server, wait until the server has received and aggregated it from all clients.