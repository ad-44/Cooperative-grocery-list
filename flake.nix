{
  description = "Python development environment for data analysis";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-26.05";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs {inherit system; };
      python = pkgs.python313.withPackages (ps: [
        ps.numpy
        ps.pandas
        ps.jupyter-console
        ps.python-lsp-server
        ps.altair
        ps.itables
        ps.tabulate
        ps.streamlit
        ps.gspread
        ps.google-auth
      ]);

      pythonrc = pkgs.writeText "pythonrc.py" ''
        import pandas as pd
        import subprocess
        from tabulate import tabulate
        import tempfile
        
        def pt(df):
          print(tabulate(df, headers="keys", tablefmt="psql"))

         def get_repl_pane():
    out = subprocess.check_output(
        [
            "tmux", "list-panes", "-a", "-F", "#{pane_id} #{pane_title}"
        ], text=True
    )

    for line in out.splitlines():
        pane_id, title = line.split(" ",1)
        if title == "REPL":
            return pane_id

    return None

def get_right_pane(repl_pane):
    out = subprocess.check_output(
        [
            "tmux", "list-panes", "-a", "-F", "#{pane_id} #{pane_left} #{pane_top}"
        ], text=True
    )

    panes = []
    for line in out.splitlines():
        pid, left, top = line.split()
        panes.append(pid)

    try:
        idx = panes.index(repl_pane)
        return panes[idx + 1]
    except:
        return None 
    
def vd(df):
    path = tempfile.mktemp(suffix='.csv')
    df.to_csv(path, index=False)

    repl = get_repl_pane()
    if not repl:
        raise RuntimeError("REPL pane does not exist")

    vd_pane = get_right_pane(repl)

    if not vd_pane:
        subprocess.run(
            [
                "tmux", "split-window", "-h", "-t", repl, f"vd {path}"
            ]
        )
        return

    subprocess.run(
        [
            "tmux", "send-keys", "-t", vd_pane, f"o {path}", "Enter"
        ]
    )       
    '';

    in {
      devShells.${system}.default = pkgs.mkShell {
        packages = with pkgs; [
          python
          quarto
          black
          visidata
        ];

      shellHook = ''
        export PYTHONSTARTUP=${pythonrc}
      '';  
      };
    };
}
