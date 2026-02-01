{
  description = "Resurch - Academic paper search CLI tool";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    rust-overlay = {
      url = "github:oxalica/rust-overlay";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    crane = {
      url = "github:ipetkov/crane";
    };
  };

  outputs = { self, nixpkgs, flake-utils, rust-overlay, crane }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        overlays = [ (import rust-overlay) ];
        pkgs = import nixpkgs {
          inherit system overlays;
        };

        rustToolchain = pkgs.rust-bin.stable.latest.default.override {
          targets = [ "x86_64-unknown-linux-musl" ];
        };

        craneLib = (crane.mkLib pkgs).overrideToolchain rustToolchain;

        # Common source filtering
        src = craneLib.cleanCargoSource ./.;

        # Common arguments for builds
        commonArgs = {
          inherit src;
          strictDeps = true;

          buildInputs = with pkgs; [
            openssl
          ] ++ pkgs.lib.optionals pkgs.stdenv.isDarwin [
            pkgs.libiconv
            pkgs.darwin.apple_sdk.frameworks.Security
            pkgs.darwin.apple_sdk.frameworks.SystemConfiguration
          ];

          nativeBuildInputs = with pkgs; [
            pkg-config
          ];
        };

        # Build dependencies separately for caching
        cargoArtifacts = craneLib.buildDepsOnly commonArgs;

        # Build the package
        resurch = craneLib.buildPackage (commonArgs // {
          inherit cargoArtifacts;
        });

        # Static musl build for containers
        resurchStatic = craneLib.buildPackage (commonArgs // {
          inherit cargoArtifacts;
          CARGO_BUILD_TARGET = "x86_64-unknown-linux-musl";
          CARGO_BUILD_RUSTFLAGS = "-C target-feature=+crt-static";
        });

      in
      {
        checks = {
          inherit resurch;

          resurch-clippy = craneLib.cargoClippy (commonArgs // {
            inherit cargoArtifacts;
            cargoClippyExtraArgs = "--all-targets -- --deny warnings";
          });

          resurch-fmt = craneLib.cargoFmt {
            inherit src;
          };
        };

        packages = {
          default = resurch;
          resurch = resurch;
          resurch-static = resurchStatic;

          # OCI container image
          container = pkgs.dockerTools.buildLayeredImage {
            name = "resurch";
            tag = "latest";
            contents = [ resurchStatic ];
            config = {
              Cmd = [ "/bin/resurch" ];
              WorkingDir = "/data";
              Volumes = { "/data" = { }; };
            };
          };
        };

        apps.default = flake-utils.lib.mkApp {
          drv = resurch;
        };

        devShells.default = craneLib.devShell {
          checks = self.checks.${system};

          packages = with pkgs; [
            rust-analyzer
            cargo-watch
            sqlite
          ];

          RUST_LOG = "resurch=debug";
        };
      }
    );
}
