# To learn more about how to use Nix to configure your environment
# see: https://developers.google.com/idx/guides/customize-idx-env
{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-24.05"; # or "unstable"
  packages = [ pkgs.python3 ];
  services.docker.enable = true;

  idx = {
    # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
    extensions = [ "ms-python.python" "rangav.vscode-thunder-client" ];
    workspace = {
      # Runs when a workspace is first created with this `dev.nix` file
      onCreate = {
        install = "chmod +x setup.sh && ./setup.sh";
        default.openFiles = [ "app/__init__.py" ];
        web = {
          # command = [ "python3" "src/main.py" ];
          # manager = "web";
          # env = {
          #   PORT = "$PORT";
          # };
        };
      };


    };
  };
}
