package main

import (
	"fmt"
	"io"
	"net"
	"os"
)

func main() {
	listenAddr := "127.0.0.1:3939"

	listener, err := net.Listen("tcp", listenAddr)
	if err != nil {
		fmt.Println("Error starting server:", err)
		os.Exit(1)
	}
	defer listener.Close()

	fmt.Println("Listening on", listenAddr)
	for {
		conn, err := listener.Accept()
		if err != nil {
			fmt.Println("Error accepting connection:", err)
			continue
		}

		fmt.Println("Client connected:", conn.RemoteAddr())
		go handleConnection(conn)
	}
}

func handleConnection(conn net.Conn) {
	defer conn.Close()
	go io.Copy(conn, os.Stdin)
	io.Copy(os.Stdout, conn)
}
