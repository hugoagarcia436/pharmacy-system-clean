# Lab Procedure

## Step 1: Open the Linux Terminal

```text
Ctrl + Alt + T
```

A Linux terminal was opened.

**Image explanation:** The image shows the terminal at the start of the lab procedure.

## Step 2: Create the First POSIX Thread

```bash
nano pthread01.c
```

```c
#include <stdio.h>
#include <pthread.h>

void *work() {
    printf("Hello world!\n");
    return NULL;
}

int main(int argc, char **argv) {
    pthread_t thread1;

    pthread_create(&thread1, NULL, work, NULL);

    return 0;
}
```

```bash
gcc -pthread pthread01.c -o pthread01
./pthread01
```

In this step, the first POSIX thread was created using `pthread_create`. The new thread was assigned to run the `work` function. When the program executed, the message did not always appear because the main program ended immediately after creating the thread. This showed that creating a thread does not automatically make the main thread wait for it.

The `pthread_t` variable stored the thread identifier, and the `work` function used the required thread-function format: it returned `void *` and received a `void *` argument. The `pthread_create` call received four arguments: the address of the thread identifier, default thread attributes through `NULL`, the function to run, and `NULL` for no argument being passed to the thread.

**Image explanation:** The screenshot should show the program being compiled and executed. If no output appears, that supports the observation that the main thread exited too quickly.

## Step 3: Use `sleep` to Keep the Process Alive

```c
#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

void *work() {
    printf("Hello world! (from the created thread)\n");
    return NULL;
}

int main(int argc, char **argv) {
    pthread_t thread1;

    pthread_create(&thread1, NULL, work, NULL);

    sleep(5);
    printf("Main thread is now exiting after waiting 5s.\n");

    return 0;
}
```

```bash
gcc -pthread pthread01.c -o pthread01
./pthread01
```

The `sleep(5)` function was added so the main thread would pause before exiting. During those five seconds, the process stayed alive, which gave the created thread enough time to run and print its message. This worked, but it was not a good synchronization method because the correct waiting time is not always known.

The result showed that the worker thread could finish while the main thread was blocked. However, this method only delayed the main thread blindly. If the worker thread took longer than five seconds, the same early-exit problem could still happen.

**Image explanation:** The screenshot should show the thread message appearing before the main thread exits after the delay.

## Step 4: Synchronize with `pthread_join`

```c
#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

void *work() {
    sleep(5);
    printf("Hello world!\n");
    return NULL;
}

int main(int argc, char **argv) {
    pthread_t thread1;

    pthread_create(&thread1, NULL, work, NULL);
    pthread_join(thread1, NULL);

    printf("Main thread exiting cleanly after thread1 finished.\n");

    return 0;
}
```

```bash
gcc -pthread pthread01.c -o pthread01
./pthread01
```

The fixed delay was replaced with `pthread_join`. This made the main thread wait specifically for `thread1` to finish. The result was better than using `sleep` because the program waited exactly as long as the worker thread needed, then exited cleanly.

The `pthread_join(thread1, NULL)` call blocked the main thread until `thread1` terminated. This is similar in purpose to using `wait()` with processes created by `fork`, except it applies to threads. The second argument was `NULL` because no return value from the thread function was needed.

**Image explanation:** The screenshot should show the worker thread printing first, followed by the main thread exit message.

## Step 5: Monitor Threads from the Operating System

```c
#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

void *work() {
    sleep(10);
    printf("Hello world!\n");
    return NULL;
}

int main(int argc, char **argv) {
    pthread_t thread1;
    int ret;

    printf("Process ID: %d\n", getpid());
    printf("Before creation of thread\n");

    ret = pthread_create(&thread1, NULL, work, NULL);

    if (ret == 0)
        printf("Thread created successfully\n");
    else
        printf("Problem in creating thread\n");

    pthread_join(thread1, NULL);
    printf("Thread terminated\n");

    return 0;
}
```

```bash
gcc -pthread pthread01.c -o pthread01
./pthread01
ps -T -p PID_VALUE
```

The process ID was printed using `getpid()`, and `ps -T -p` was then used from another terminal while the program was sleeping. The output showed multiple thread entries under the same PID. This proved that threads share one process ID, but the operating system still tracks each thread separately using thread IDs.

The longer `sleep(10)` gave enough time to inspect the running program before it ended. The expected `ps` output contained one entry for the main thread and one entry for the created thread. The PID stayed the same, while the thread IDs were different, showing that Linux represents threads as separate lightweight execution units inside one process.

**Image explanation:** The screenshot should show the first terminal with the PID and the second terminal showing the `ps -T -p` output with the main thread and worker thread.

## Step 6: Create Multiple Threads

```c
#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

void *work() {
    sleep(10);
    printf("Hello world!\n");
    return NULL;
}

int main(int argc, char **argv) {
    pthread_t thread1, thread2;

    printf("Process ID: %d\n", getpid());

    pthread_create(&thread1, NULL, work, NULL);
    pthread_create(&thread2, NULL, work, NULL);

    pthread_join(thread1, NULL);
    pthread_join(thread2, NULL);

    printf("All threads have terminated. Exiting.\n");

    return 0;
}
```

```bash
gcc -pthread pthread01.c -o pthread01
./pthread01
ps -T -p PID_VALUE
```

Two worker threads were created to execute the same function. While the program was running, the `ps` command showed three execution entries: the main thread and two worker threads. Even though both worker threads slept for ten seconds, the total runtime stayed close to ten seconds because the threads ran concurrently instead of one after the other.

Two `pthread_t` variables were needed because each thread required its own identifier. Two `pthread_join` calls were also needed so the main thread waited for both worker threads. If one thread had already finished by the time its join was reached, the join returned immediately.

**Image explanation:** The screenshot should show three rows in the `ps -T -p` output for one process.

## Step 7: Run Different Tasks in Different Threads

```c
#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

void *work() {
    sleep(10);
    printf("Hello world 1! (Task A finished)\n");
    return NULL;
}

void *work2() {
    sleep(10);
    printf("Hello world 2! (Task B finished)\n");
    return NULL;
}

int main(int argc, char **argv) {
    pthread_t thread1, thread2;

    printf("Process ID: %d\n", getpid());

    pthread_create(&thread1, NULL, work, NULL);
    pthread_create(&thread2, NULL, work2, NULL);

    pthread_join(thread1, NULL);
    pthread_join(thread2, NULL);

    printf("Both different tasks are done. Exiting.\n");

    return 0;
}
```

The program was modified so each thread ran a different function. Both tasks ran at the same time, but the order of the printed messages was not guaranteed. The scheduler decides which thread runs first, so either message could appear first.

This step demonstrated that threads do not have to run the same routine. One thread executed `work`, and the other executed `work2`. Even though both functions had the same sleep time, the output order depended on the operating system scheduler, so `Hello world 1` was not guaranteed to appear before `Hello world 2`.

**Image explanation:** The screenshot should show both task messages and the final message after both joins complete.

## Step 8: Compare Processes and Threads

```c
/* processes.c */
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/types.h>

int main(int argc, char *argv[]) {
    int pid = fork();

    if (pid == -1)
        return 1;

    printf("Hello from processes\n");

    if (pid != 0)
        wait(NULL);

    return 0;
}
```

```c
/* threads.c */
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <pthread.h>

void *routine() {
    printf("Hello from threads\n");
    return NULL;
}

int main(int argc, char *argv[]) {
    pthread_t t1, t2;

    pthread_create(&t1, NULL, routine, NULL);
    pthread_create(&t2, NULL, routine, NULL);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    return 0;
}
```

```bash
gcc processes.c -o processes
./processes
gcc -pthread threads.c -o threads
./threads
```

One program was created using `fork`, and another was created using threads. Both programs printed two messages, but they achieved concurrency differently. The process program created a child process with a separate memory space, while the thread program created two threads inside the same process.

The process program printed one message from the parent and one from the child because `fork()` returns once in each process. The thread program printed one message from each created thread because `pthread_create` starts a specific function in a new thread. The outputs looked similar, but the memory architecture behind them was different.

**Image explanation:** The screenshot should show both programs running and producing two printed lines each.

## Step 9: Verify Process IDs

```c
/* processes.c */
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/types.h>

int main(int argc, char *argv[]) {
    int pid = fork();

    if (pid == -1)
        return 1;

    printf("Process PID: %d\n", getpid());

    if (pid != 0)
        wait(NULL);

    return 0;
}
```

```c
/* threads.c */
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <pthread.h>

void *routine() {
    printf("Thread belonging to PID: %d\n", getpid());
    return NULL;
}

int main(int argc, char *argv[]) {
    pthread_t t1, t2;

    pthread_create(&t1, NULL, routine, NULL);
    pthread_create(&t2, NULL, routine, NULL);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    return 0;
}
```

When the PID was printed in the process program, two different process IDs appeared because `fork` creates a separate child process. In the thread program, both threads printed the same PID because they belonged to the same process.

This confirmed the difference between processes and threads. Processes receive separate PIDs from the operating system, while threads remain inside the same PID. Even when threads share a PID, Linux can still distinguish them internally by thread ID, as shown earlier with the `ps -T -p` command.

**Image explanation:** The screenshot should show different PIDs for the process program and the same PID repeated for the thread program.

## Step 10: Observe Memory Isolation in Processes

```c
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/types.h>

int main(int argc, char *argv[]) {
    int x = 2;
    int pid = fork();

    if (pid == -1)
        return 1;

    if (pid == 0) {
        x++;
        printf("Child is incrementing x...\n");
    }

    sleep(2);
    printf("Process id: %d | Value of x: %d\n", getpid(), x);

    if (pid != 0)
        wait(NULL);

    return 0;
}
```

Only the child process incremented `x`. The child printed `x` as 3, but the parent still printed `x` as 2. This happened because after `fork`, the parent and child have separate memory spaces.

The variable `x` began with the value 2 before the fork. After the fork, the child process had its own copy and incremented only that copy. The parent process kept its original copy, so a change in the child did not affect the parent.

**Image explanation:** The screenshot should show two different PIDs and two different values for `x`.

## Step 11: Test a Global Variable with Processes

```c
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/types.h>

int x = 2;

int main(int argc, char *argv[]) {
    int pid = fork();

    if (pid == -1)
        return 1;

    if (pid == 0) {
        x++;
    }

    sleep(2);
    printf("Process id: %d | Global x: %d\n", getpid(), x);

    if (pid != 0)
        wait(NULL);

    return 0;
}
```

The variable `x` was moved outside of `main` to make it global. The result was still the same: the child saw the changed value, while the parent kept the original value. This showed that `fork` duplicates the whole address space, including global variables.

Making `x` global did not make it shared between the parent and child. The forked child still received a separate copy of the stack, heap, and static/data segment. As a result, a global variable could not be used by itself for communication between these two processes.

**Image explanation:** The screenshot should show that the parent and child still print different values for the global variable.

## Step 12: Share Memory Between Threads

```c
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <pthread.h>

int x = 2;

void *routine() {
    x++;
    sleep(2);
    printf("Thread 1 sees x as: %d\n", x);
    return NULL;
}

void *routine2() {
    sleep(2);
    printf("Thread 2 sees x as: %d\n", x);
    return NULL;
}

int main(int argc, char *argv[]) {
    pthread_t t1, t2;

    pthread_create(&t1, NULL, routine, NULL);
    pthread_create(&t2, NULL, routine2, NULL);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    return 0;
}
```

Both threads shared the same global variable `x`. When the first thread incremented `x`, the second thread saw the updated value. This confirmed that threads share memory inside the same process, which makes communication easier but also creates risk when multiple threads modify the same data.

This behavior was the opposite of the process examples. In the threaded program, there was only one global `x` in the process address space. Both thread routines accessed that same memory location, so the update made by one thread was visible to the other.

**Image explanation:** The screenshot should show both threads printing the same updated value of `x`.

## Step 13: Create a Shared Counter

```c
#include <stdlib.h>
#include <stdio.h>
#include <pthread.h>

int mails = 0;

void *routine() {
    mails++;
    return NULL;
}

int main(int argc, char *argv[]) {
    pthread_t t1, t2;

    pthread_create(&t1, NULL, routine, NULL);
    pthread_create(&t2, NULL, routine, NULL);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    printf("Number of emails: %d\n", mails);

    return 0;
}
```

A shared variable named `mails` was created, and two threads incremented it once. The expected result was 2, and the program usually produced that value because the amount of work was very small.

This step introduced a shared counter that both threads could modify. Since the operation happened only once per thread, the result appeared correct, but the counter was still being accessed without synchronization.

**Image explanation:** The screenshot should show the final counter value printed as 2.

## Step 14: Increment the Counter with a Small Loop

```c
#include <stdlib.h>
#include <stdio.h>
#include <pthread.h>

int mails = 0;

void *routine() {
    for (int i = 0; i < 100; i++) {
        mails++;
    }
    return NULL;
}

int main(int argc, char *argv[]) {
    pthread_t t1, t2;

    pthread_create(&t1, NULL, routine, NULL);
    pthread_create(&t2, NULL, routine, NULL);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    printf("Number of emails: %d\n", mails);

    return 0;
}
```

Each thread incremented the shared counter 100 times, so the expected value was 200. The result often appeared correct because the loop was short and the CPU could finish one thread quickly. However, the shared variable was still unprotected.

This showed that a race condition may not appear clearly when the workload is small. The program could still be unsafe even when the displayed result looked correct.

**Image explanation:** The screenshot should show the counter result, which will likely be 200.

## Step 15: Demonstrate a Race Condition

```c
#include <stdlib.h>
#include <stdio.h>
#include <pthread.h>

int mails = 0;

void *routine() {
    for (int i = 0; i < 1000000; i++) {
        mails++;
    }
    return NULL;
}

int main(int argc, char *argv[]) {
    pthread_t t1, t2;

    pthread_create(&t1, NULL, routine, NULL);
    pthread_create(&t2, NULL, routine, NULL);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    printf("Number of emails: %d\n", mails);

    return 0;
}
```

With one million increments per thread, the expected result was 2,000,000. The actual result changed between runs and was usually lower. This happened because `mails++` is not atomic. The CPU reads the value, increments it, and writes it back. If two threads overlap during those steps, one update can overwrite another.

The shared line `mails++` became the critical section because both threads were reading and writing the same variable. The lost updates happened when one thread read an old value while another thread was also modifying it. The final number depended on timing and scheduling, so it was not deterministic.

**Image explanation:** The screenshot should show the final counter value being less than 2,000,000 or changing after multiple executions.

## Step 16: Fix the Race Condition with a Mutex

```c
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <pthread.h>

int mails = 0;
pthread_mutex_t mutex;

void *routine() {
    for (int i = 0; i < 1000000; i++) {
        pthread_mutex_lock(&mutex);
        mails++;
        pthread_mutex_unlock(&mutex);
    }
    return NULL;
}

int main(int argc, char *argv[]) {
    pthread_t t1, t2;

    pthread_mutex_init(&mutex, NULL);

    pthread_create(&t1, NULL, routine, NULL);
    pthread_create(&t2, NULL, routine, NULL);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    pthread_mutex_destroy(&mutex);

    printf("Number of mails: %d\n", mails);

    return 0;
}
```

The shared counter was protected with a mutex. Only one thread could enter the critical section at a time, so the increment operation became safe. The final result became exactly 2,000,000 every time.

The mutex was declared globally, initialized before the threads were created, locked before `mails++`, unlocked immediately after `mails++`, and destroyed after the threads finished. Locking the mutex made the read-modify-write sequence behave as one protected operation from the perspective of the other thread. The program could run slightly slower because the threads had to wait for each other at the lock.

**Image explanation:** The screenshot should show the final result as exactly 2,000,000.

## Step 17: Scale the Mutex Solution to Four Threads

```c
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <pthread.h>

int mails = 0;
pthread_mutex_t mutex;

void *routine() {
    for (int i = 0; i < 1000000; i++) {
        pthread_mutex_lock(&mutex);
        mails++;
        pthread_mutex_unlock(&mutex);
    }
    return NULL;
}

int main(int argc, char *argv[]) {
    pthread_t t1, t2, t3, t4;

    pthread_mutex_init(&mutex, NULL);

    pthread_create(&t1, NULL, routine, NULL);
    pthread_create(&t2, NULL, routine, NULL);
    pthread_create(&t3, NULL, routine, NULL);
    pthread_create(&t4, NULL, routine, NULL);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    pthread_join(t3, NULL);
    pthread_join(t4, NULL);

    pthread_mutex_destroy(&mutex);

    printf("Number of mails: %d\n", mails);

    return 0;
}
```

The number of threads was increased from two to four. Since each thread incremented the counter one million times, the correct answer was 4,000,000. The mutex kept the result correct even with more threads, although the program could take longer because all four threads had to wait for the same lock.

This step showed that the mutex solution scales in correctness. The same locking logic protected the shared counter no matter how many threads were created. The trade-off was increased contention because more threads were competing for the same mutex.

**Image explanation:** The screenshot should show the final result as exactly 4,000,000.

## Step 18: Remove the Lock to Verify the Problem

```c
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <pthread.h>

int mails = 0;
pthread_mutex_t mutex;

void *routine() {
    for (int i = 0; i < 1000000; i++) {
        /* pthread_mutex_lock(&mutex); */
        mails++;
        /* pthread_mutex_unlock(&mutex); */
    }
    return NULL;
}

int main(int argc, char *argv[]) {
    pthread_t t1, t2, t3, t4;

    pthread_mutex_init(&mutex, NULL);

    pthread_create(&t1, NULL, routine, NULL);
    pthread_create(&t2, NULL, routine, NULL);
    pthread_create(&t3, NULL, routine, NULL);
    pthread_create(&t4, NULL, routine, NULL);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    pthread_join(t3, NULL);
    pthread_join(t4, NULL);

    pthread_mutex_destroy(&mutex);

    printf("Number of mails: %d\n", mails);

    return 0;
}
```

The lock and unlock calls were commented out while keeping four threads. The program ran without protection, so the final value became incorrect again and changed between executions. This confirmed that the mutex was responsible for preserving data integrity.

With four threads, the race condition became more severe because the chance of multiple threads reading the same value at the same time increased. The program could appear faster without locking, but the result was wrong. This demonstrated the trade-off between speed and correctness in concurrent programming.

**Image explanation:** The screenshot should show a final result below 4,000,000, ideally after running the program more than once to show that the number changes.

## Step 19: Create a Semaphore Program

```bash
nano semaphores.c
```

```c
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <pthread.h>
#include <string.h>
#include <semaphore.h>

#define THREAD_NUM 4

sem_t semaphore;

void *routine(void *args) {
    printf("Hello from thread %d\n", *(int *)args);
    free(args);
    return NULL;
}

int main(int argc, char *argv[]) {
    pthread_t th[THREAD_NUM];

    sem_init(&semaphore, 0, 1);

    for (int i = 0; i < THREAD_NUM; i++) {
        int *a = malloc(sizeof(int));
        *a = i;

        if (pthread_create(&th[i], NULL, routine, a) != 0) {
            perror("Failed to create thread");
        }
    }

    for (int i = 0; i < THREAD_NUM; i++) {
        if (pthread_join(th[i], NULL) != 0) {
            perror("Failed to join thread");
        }
    }

    sem_destroy(&semaphore);

    return 0;
}
```

```bash
gcc -pthread semaphores.c -o semaphores
./semaphores
```

A semaphore and four threads were created. Each thread received its own dynamically allocated ID using `malloc`. The semaphore was initialized, but it was not used yet with `sem_wait` or `sem_post`, so the threads printed freely.

The semaphore type was `sem_t`. The call `sem_init(&semaphore, 0, 1)` initialized the semaphore for use between threads in the same process, with an initial counter value of 1. The dynamic allocation for the thread argument prevented all threads from accidentally reading the same loop variable after the loop changed.

**Image explanation:** The screenshot should show four thread messages. The order may vary because the threads run concurrently.

## Step 20: Add `sem_wait` and `sem_post`

```c
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <pthread.h>
#include <string.h>
#include <semaphore.h>

#define THREAD_NUM 4

sem_t semaphore;

void *routine(void *args) {
    sem_wait(&semaphore);
    sleep(1);
    printf("Hello from thread %d\n", *(int *)args);
    sem_post(&semaphore);

    free(args);
    return NULL;
}

int main(int argc, char *argv[]) {
    pthread_t th[THREAD_NUM];

    sem_init(&semaphore, 0, 1);

    for (int i = 0; i < THREAD_NUM; i++) {
        int *a = malloc(sizeof(int));
        *a = i;

        if (pthread_create(&th[i], NULL, routine, a) != 0) {
            perror("Fail to create thread");
        }
    }

    for (int i = 0; i < THREAD_NUM; i++) {
        if (pthread_join(th[i], NULL) != 0) {
            perror("Fail to join thread");
        }
    }

    sem_destroy(&semaphore);

    return 0;
}
```

The `sem_wait` call was added before the critical section, and `sem_post` was added after it. Since the semaphore started with a value of 1, only one thread could pass through at a time. The one-second sleep made the serialized behavior easy to observe.

In semaphore terminology, `sem_wait` corresponds to the P operation and decreases the semaphore counter. If the counter is 0, the thread blocks. The `sem_post` call corresponds to the V operation and increases the counter, allowing another blocked thread to continue.

**Image explanation:** The screenshot should show one thread message appearing at a time, with a delay between messages.

## Step 21: Restrict Access with a Binary Semaphore

```c
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <pthread.h>
#include <string.h>
#include <semaphore.h>

#define THREAD_NUM 4

sem_t semaphore;

void *routine(void *args) {
    sem_wait(&semaphore);

    sleep(1);
    printf("Hello from thread %d\n", *(int *)args);

    sem_post(&semaphore);

    free(args);
    return NULL;
}

int main(int argc, char *argv[]) {
    pthread_t th[THREAD_NUM];

    sem_init(&semaphore, 0, 1);

    for (int i = 0; i < THREAD_NUM; i++) {
        int *a = malloc(sizeof(int));
        *a = i;

        if (pthread_create(&th[i], NULL, routine, a) != 0) {
            perror("Failed to create thread");
        }
    }

    for (int i = 0; i < THREAD_NUM; i++) {
        if (pthread_join(th[i], NULL) != 0) {
            perror("Failed to join thread");
        }
    }

    sem_destroy(&semaphore);

    return 0;
}
```

This version used the semaphore like a mutex because the initial value was 1. The first thread reduced the value to 0 and entered the protected section. The remaining threads had to wait until `sem_post` increased the value again. The program took about four seconds because the four threads passed through one at a time.

Although all four threads were created almost at the same time, the semaphore created a bottleneck at the print section. In this configuration, the semaphore provided mutual exclusion, so its behavior was functionally similar to a mutex.

**Image explanation:** The screenshot should show the four messages appearing sequentially, not all at once.

## Step 22: Use a Counting Semaphore

```c
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <pthread.h>
#include <string.h>
#include <semaphore.h>

#define THREAD_NUM 4

sem_t semaphore;

void *routine(void *args) {
    sem_wait(&semaphore);

    sleep(1);
    printf("Hello from thread %d\n", *(int *)args);

    sem_post(&semaphore);

    free(args);
    return NULL;
}

int main(int argc, char *argv[]) {
    pthread_t th[THREAD_NUM];

    sem_init(&semaphore, 0, 3);

    for (int i = 0; i < THREAD_NUM; i++) {
        int *a = malloc(sizeof(int));
        *a = i;

        if (pthread_create(&th[i], NULL, routine, a) != 0) {
            perror("Failed to create thread");
        }
    }

    for (int i = 0; i < THREAD_NUM; i++) {
        if (pthread_join(th[i], NULL) != 0) {
            perror("Failed to join thread");
        }
    }

    sem_destroy(&semaphore);

    return 0;
}
```

The semaphore initial value was changed from 1 to 3. This allowed three threads to enter the protected section at the same time. The fourth thread waited until one of the first three called `sem_post`. This demonstrated the main difference between a mutex and a counting semaphore: a mutex allows one thread at a time, while a semaphore can allow a limited number of threads at once.

The output was expected to appear in two groups. The first three thread messages could appear close together because three permits were available. The last thread had to wait until one permit was returned. This showed how changing the initial semaphore value changes the amount of concurrency allowed.

**Image explanation:** The screenshot should show the first group of thread messages appearing close together, followed by the last thread after one of the semaphore slots becomes available.
