# Lab 03 Procedure Explanation: Concurrency and Synchronization

## Part I: Thread Fundamentals and Lifecycle

### Step 1: Opening the Linux terminal

```bash
Ctrl + Alt + T
```

I started by opening a Linux terminal so I could create, compile, and run C programs directly from the command line. This was necessary because the lab uses POSIX threads, process commands, and Linux tools such as `ps`.

### Step 2: Creating the first POSIX thread

```bash
nano pthread01.c
```

```c
#include <stdio.h>
#include <pthread.h>

void *work(void *arg) {
    printf("Hello world!\n");
    return NULL;
}

int main(int argc, char *argv[]) {
    pthread_t thread1;

    pthread_create(&thread1, NULL, work, NULL);
    printf("Main thread exiting clearly after pthread_create.\n");

    return 0;
}
```

```bash
gcc -pthread pthread01.c -o pthread01
./pthread01
```

I created a C file and used `pthread_create` to start a new thread that runs the `work` function. The important observation was that creating a thread is not the same as calling a normal function. The main thread continued immediately after `pthread_create`, printed its own message, and then ended.

In the screenshot for this step, the nano editor shows the first version of `pthread01.c`. The terminal output image shows the program compiling and running, but the worker thread message does not reliably appear. This happened because the main thread exited before the new thread had enough time to run.

### Step 3: Keeping the process alive with `sleep`

```c
#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

void *work(void *arg) {
    printf("Hello world!\n");
    return NULL;
}

int main(int argc, char *argv[]) {
    pthread_t thread1;

    pthread_create(&thread1, NULL, work, NULL);
    sleep(5);
    printf("Main thread exiting clearly after thread1 finished.\n");

    return 0;
}
```

```bash
gcc -pthread pthread03.c -o pthread03
./pthread03
```

I added `sleep(5)` after creating the thread. During those five seconds, the main thread was paused, but the process was still alive, so the worker thread had time to print `Hello world!`.

The screenshot shows that `Hello world!` appears before the final main-thread message. The result proves that the worker thread did run, but this is only a temporary solution. Sleeping is not reliable synchronization because a real task might take less or more time than the chosen delay.

### Step 4: Synchronizing with `pthread_join`

```c
#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

void *work(void *arg) {
    sleep(5);
    printf("Hello world!\n");
    return NULL;
}

int main(int argc, char *argv[]) {
    pthread_t thread1;

    pthread_create(&thread1, NULL, work, NULL);
    pthread_join(thread1, NULL);
    printf("Main thread exiting clearly after thread1 finished.\n");

    return 0;
}
```

```bash
gcc -pthread pthread03.c -o pthread03
./pthread03
```

I replaced the fixed delay with `pthread_join`. This made the main thread wait for `thread1` specifically. Unlike `sleep`, `pthread_join` does not guess how long the thread needs; it waits until the target thread actually finishes.

The screenshot shows the worker message first and the main-thread exit message afterward. The result confirms correct synchronization: the program no longer exits prematurely, and it does not wait longer than necessary after the worker completes.

### Step 5: Viewing threads from the operating system

```c
#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

void *work(void *arg) {
    sleep(10);
    printf("Hello world!\n");
    return NULL;
}

int main(int argc, char *argv[]) {
    pthread_t thread1;

    pthread_create(&thread1, NULL, work, NULL);
    printf("Process ID: %d\n", getpid());
    printf("The thread is sleeping for 10 seconds...\n");
    pthread_join(thread1, NULL);
    printf("Thread terminated.\n");

    return 0;
}
```

```bash
gcc -pthread pthread01.c -o pthread01
./pthread01
ps -T -p <process_id>
```

I printed the process ID with `getpid()` and kept the thread alive long enough to inspect it from another terminal. Then I used `ps -T -p <process_id>` to list the threads inside that process.

The screenshot shows one process ID with two thread entries. One entry belongs to the main thread, and the other belongs to the worker thread. This proves that the operating system treats threads as separate execution units even though they belong to the same process.

### Step 6: Creating multiple threads with the same task

```c
#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

void *work(void *arg) {
    sleep(10);
    printf("Hello world!\n");
    return NULL;
}

int main(int argc, char *argv[]) {
    pthread_t thread1, thread2;

    pthread_create(&thread1, NULL, work, NULL);
    pthread_create(&thread2, NULL, work, NULL);

    printf("Process ID: %d\n", getpid());
    printf("All threads have been created, waiting...\n");

    pthread_join(thread1, NULL);
    pthread_join(thread2, NULL);

    printf("All threads terminated. Exiting.\n");
    return 0;
}
```

```bash
gcc -pthread pthread01.c -o pthread01
./pthread01
ps -T -p <process_id>
```

I created two worker threads that both ran the same `work` function. I also used two `pthread_join` calls so the main thread would wait for both of them.

The screenshot with `ps -T` shows three thread entries under the same process ID: the main thread and two worker threads. Since both worker threads slept at the same time, the total running time stayed close to 10 seconds instead of becoming 20 seconds. That shows the two worker threads were running concurrently.

### Step 7: Running different tasks at the same time

```c
#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

void *task1(void *arg) {
    sleep(10);
    printf("Hello world 1 (Task A finished)\n");
    return NULL;
}

void *task2(void *arg) {
    sleep(10);
    printf("Hello world 2 (Task B finished)\n");
    return NULL;
}

int main(int argc, char *argv[]) {
    pthread_t thread1, thread2;

    pthread_create(&thread1, NULL, task1, NULL);
    pthread_create(&thread2, NULL, task2, NULL);

    printf("Process ID: %d\n", getpid());
    printf("Program is running, threads are sleeping for 10 seconds...\n");

    pthread_join(thread1, NULL);
    pthread_join(thread2, NULL);

    printf("Both different tasks are done. Exiting.\n");
    return 0;
}
```

```bash
gcc -pthread pthread01.c -o pthread01
./pthread01
```

I changed the program so each thread ran a different function. This simulated two independent tasks happening in the same process.

The screenshots show both task messages after the sleep period. In one run, task 1 printed before task 2, but that order is not guaranteed. Since the scheduler controls when each thread runs, either task could finish first if their timing is close.

## Part II: Threads vs. Processes and Memory Architecture

### Step 8: Comparing a process program with a thread program

```c
/* fork.c */
#include <stdio.h>
#include <unistd.h>

int main(void) {
    fork();
    printf("Hello world!\n");
    return 0;
}
```

```c
/* threads.c */
#include <stdio.h>
#include <pthread.h>

void *routine(void *arg) {
    printf("Hello world!\n");
    return NULL;
}

int main(void) {
    pthread_t t1, t2;

    pthread_create(&t1, NULL, routine, NULL);
    pthread_create(&t2, NULL, routine, NULL);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    return 0;
}
```

```bash
gcc fork.c -o fork
gcc -pthread threads.c -o threads
./fork
./threads
```

I wrote one program using `fork()` and another using `pthread_create`. Both programs produced two messages, so the output looked similar at first.

The important difference is how the concurrency was created. In the process version, `fork()` duplicated the process. In the thread version, the two execution paths stayed inside the same process.

### Step 9: Checking process IDs

```c
/* fork.c */
#include <stdio.h>
#include <unistd.h>

int main(void) {
    fork();
    printf("Process ID: %d\n", getpid());
    return 0;
}
```

```c
/* threads.c */
#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

void *routine(void *arg) {
    printf("Thread belonging to PID: %d\n", getpid());
    return NULL;
}

int main(void) {
    pthread_t t1, t2;

    pthread_create(&t1, NULL, routine, NULL);
    pthread_create(&t2, NULL, routine, NULL);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    return 0;
}
```

```bash
gcc fork.c -o fork
gcc -pthread threads.c -o threads
./fork
./threads
```

I added `getpid()` to both programs. The process program printed two different process IDs because `fork()` created a parent and child process. The thread program printed the same process ID twice because both threads lived inside one process.

The screenshots support this difference. The `fork` output shows separate PIDs for the parent and child. The thread output shows both threads belonging to the same PID.

### Step 10: Memory isolation in processes

```c
#include <stdio.h>
#include <unistd.h>

int main(void) {
    int x = 2;
    pid_t pid = fork();

    if (pid == 0) {
        x++;
    }

    printf("Process id: %d | X: %d\n", getpid(), x);
    return 0;
}
```

```bash
gcc fork.c -o fork
./fork
```

I created a local variable `x` before calling `fork()`. The child process incremented `x`, but the parent did not.

The result showed the child with `x = 3` and the parent with `x = 2`. This proves that after `fork()`, each process has its own private copy of memory. A variable changed in the child process does not change the parent process's version.

### Step 11: Testing a global variable with processes

```c
#include <stdio.h>
#include <unistd.h>

int x = 2;

int main(void) {
    pid_t pid = fork();

    if (pid == 0) {
        x++;
    }

    printf("Process id: %d | Global X: %d\n", getpid(), x);
    return 0;
}
```

```bash
gcc fork.c -o fork
./fork
```

I moved `x` outside of `main` to make it global. The result was still the same: the child printed the incremented value, and the parent printed the original value.

The screenshot shows one process with `Global X: 3` and another with `Global X: 2`. This means global variables are also copied during `fork()`. Global scope does not make a variable shared between separate processes.

### Step 12: Shared global variables in threads

```c
#include <stdio.h>
#include <pthread.h>

int x = 2;

void *routine(void *arg) {
    x++;
    printf("Thread 1 (routine) sees x as: %d\n", x);
    return NULL;
}

void *routine2(void *arg) {
    printf("Thread 2 (routine2) sees x as: %d\n", x);
    return NULL;
}

int main(void) {
    pthread_t t1, t2;

    pthread_create(&t1, NULL, routine, NULL);
    pthread_join(t1, NULL);

    pthread_create(&t2, NULL, routine2, NULL);
    pthread_join(t2, NULL);

    return 0;
}
```

```bash
gcc -pthread threads.c -o threads
./threads
```

I used a global variable with two threads. The first thread incremented `x`, and the second thread printed it.

The screenshot shows both threads seeing `x` as `3`. This proves that threads share the same address space. Sharing memory makes communication easier than with processes, but it also creates the possibility of race conditions when multiple threads modify the same variable.

## Part III: Critical Section and Race Condition

### Step 13: Basic shared counter

```c
#include <stdio.h>
#include <pthread.h>

int mails = 0;

void *routine(void *arg) {
    mails++;
    return NULL;
}

int main(void) {
    pthread_t t1, t2;

    pthread_create(&t1, NULL, routine, NULL);
    pthread_create(&t2, NULL, routine, NULL);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    printf("Number of mails: %d\n", mails);
    return 0;
}
```

```bash
gcc -pthread threads.c -o threads
./threads
```

I created a shared counter named `mails` and had two threads increment it once each. The expected value was `2`, and the program normally reached that value because the workload was extremely small.

### Step 14: Incrementing the counter 100 times per thread

```c
#include <stdio.h>
#include <pthread.h>

int mails = 0;

void *routine(void *arg) {
    for (int i = 0; i < 100; i++) {
        mails++;
    }
    return NULL;
}

int main(void) {
    pthread_t t1, t2;

    pthread_create(&t1, NULL, routine, NULL);
    pthread_create(&t2, NULL, routine, NULL);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    printf("Number of mails: %d\n", mails);
    return 0;
}
```

```bash
gcc -pthread threads.c -o threads
./threads
```

I increased the work to 100 increments per thread. The expected total was `200`.

The screenshot shows `Number of mails: 200`. This result was correct because the loop was still short, so there was less chance for the operating system to interrupt both threads during the same increment operation.

### Step 15: Race condition with 1,000,000 increments

```c
#include <stdio.h>
#include <pthread.h>

int mails = 0;

void *routine(void *arg) {
    for (int i = 0; i < 1000000; i++) {
        mails++;
    }
    return NULL;
}

int main(void) {
    pthread_t t1, t2;

    pthread_create(&t1, NULL, routine, NULL);
    pthread_create(&t2, NULL, routine, NULL);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    printf("Number of mails: %d\n", mails);
    return 0;
}
```

```bash
gcc -pthread threads.c -o threads
./threads
```

I increased the loop to 1,000,000 increments per thread. The expected total was `2,000,000`, but the screenshots show lower values such as `1,627,341` and `1,726,431`.

This happened because `mails++` is not atomic. The CPU must read `mails`, add one, and write the result back. If two threads read the same old value before either writes back, one increment is lost. The final number changed from run to run because thread scheduling is unpredictable.

## Part IV: Thread Synchronization and Mutex

### Step 16: Protecting the counter with a mutex

```c
#include <stdio.h>
#include <pthread.h>

int mails = 0;
pthread_mutex_t mutex;

void *routine(void *arg) {
    for (int i = 0; i < 1000000; i++) {
        pthread_mutex_lock(&mutex);
        mails++;
        pthread_mutex_unlock(&mutex);
    }
    return NULL;
}

int main(void) {
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

```bash
gcc -pthread threads.c -o threads
./threads
```

I added a mutex around the increment statement. The mutex made sure only one thread could execute the critical section at a time.

The result became stable because no two threads could read, modify, and write `mails` at the same time. The trade-off is that the program may run slower because threads sometimes wait for the lock.

### Step 17: Scaling the mutex solution to four threads

```c
#include <stdio.h>
#include <pthread.h>

int mails = 0;
pthread_mutex_t mutex;

void *routine(void *arg) {
    for (int i = 0; i < 1000000; i++) {
        pthread_mutex_lock(&mutex);
        mails++;
        pthread_mutex_unlock(&mutex);
    }
    return NULL;
}

int main(void) {
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

```bash
gcc -pthread thread_mutex.c -o thread_mutex
./thread_mutex
```

I expanded the program from two threads to four threads. Each thread still incremented the counter 1,000,000 times, so the expected total was `4,000,000`.

The screenshot shows `Number of mails: 4000000`. This confirms that the mutex still protected the critical section correctly even with more threads. The main cost is more lock contention because four threads are competing for the same mutex.

### Step 18: Removing the lock to verify the race condition

```c
#include <stdio.h>
#include <pthread.h>

int mails = 0;
pthread_mutex_t mutex;

void *routine(void *arg) {
    for (int i = 0; i < 1000000; i++) {
        /* pthread_mutex_lock(&mutex); */
        mails++;
        /* pthread_mutex_unlock(&mutex); */
    }
    return NULL;
}

int main(void) {
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

```bash
gcc -pthread thread_chaos.c -o thread_chaos
./thread_chaos
```

I commented out the lock and unlock calls while keeping four threads. The expected value was still `4,000,000`, but the screenshot shows a much lower value such as `1,738,421`.

This confirms that the mutex was responsible for correctness. Without it, the program may run faster, but the result is wrong because many increments are lost.

## Part V: Semaphores and Resource Management

### Step 19: Creating threads and initializing a semaphore

```c
#include <stdio.h>
#include <pthread.h>
#include <semaphore.h>
#include <stdlib.h>

sem_t semaphore;

void *routine(void *args) {
    int id = *(int *)args;
    printf("Hello from thread %d\n", id);
    free(args);
    return NULL;
}

int main(void) {
    pthread_t th[4];
    sem_init(&semaphore, 0, 1);

    for (int i = 0; i < 4; i++) {
        int *a = malloc(sizeof(int));
        *a = i;
        pthread_create(&th[i], NULL, routine, a);
    }

    for (int i = 0; i < 4; i++) {
        pthread_join(th[i], NULL);
    }

    sem_destroy(&semaphore);
    return 0;
}
```

```bash
gcc -pthread semaphores.c -o semaphores
./semaphores
```

I created four threads and initialized a semaphore, but I did not use `sem_wait` or `sem_post` yet. Each thread received its own ID through dynamically allocated memory.

The screenshot shows the threads printing their messages freely. This happened because the semaphore existed, but it was not controlling access yet. The `malloc` call was important because passing `&i` directly could cause every thread to read the same changing loop variable.

### Step 20: Adding semaphore operations

```c
sem_wait(&semaphore);
printf("Hello from thread %d\n", id);
sem_post(&semaphore);
```

```bash
gcc -pthread semaphores.c -o semaphores
./semaphores
```

I added `sem_wait` before the protected output and `sem_post` after it. With the semaphore initialized to `1`, only one thread could enter the protected section at a time.

The screenshot shows all four thread messages, but the semaphore controls how they enter the protected area. With a value of `1`, the semaphore behaves like a mutex because it allows only one thread at a time.

### Step 21: Restricting access with `sem_wait` and `sem_post`

```c
#include <stdio.h>
#include <pthread.h>
#include <semaphore.h>
#include <stdlib.h>
#include <unistd.h>

sem_t semaphore;

void *routine(void *args) {
    int id = *(int *)args;
    free(args);

    sem_wait(&semaphore);
    sleep(1);
    printf("Hello from thread %d\n", id);
    sem_post(&semaphore);

    return NULL;
}

int main(void) {
    pthread_t th[4];
    sem_init(&semaphore, 0, 1);

    for (int i = 0; i < 4; i++) {
        int *a = malloc(sizeof(int));
        *a = i;
        pthread_create(&th[i], NULL, routine, a);
    }

    for (int i = 0; i < 4; i++) {
        pthread_join(th[i], NULL);
    }

    sem_destroy(&semaphore);
    return 0;
}
```

```bash
gcc -pthread semaphores.c -o semaphores
./semaphores
```

I placed `sleep(1)` inside the protected section. Because the semaphore value was `1`, each thread had to wait for the previous thread to finish before entering.

The screenshot shows the thread messages appearing one at a time. The whole run takes about four seconds because four threads each spend one second in the restricted section.

### Step 22: Allowing multiple threads with a counting semaphore

```c
sem_init(&semaphore, 0, 3);
```

```c
void *routine(void *args) {
    int id = *(int *)args;
    free(args);

    sem_wait(&semaphore);
    sleep(1);
    printf("Hello from thread %d\n", id);
    sem_post(&semaphore);

    return NULL;
}
```

```bash
gcc -pthread semaphores.c -o semaphores
./semaphores
```

I changed the initial semaphore value from `1` to `3`. This allowed up to three threads to enter the protected section at the same time.

The screenshots show that the output order can change, such as thread 1 printing before thread 0. That is normal because the scheduler decides which waiting thread runs next. The key result is that the first three threads can proceed together, while the fourth waits until one permit is released.

## Image Explanations

1. `image1.jpeg`: This is the UTRGV logo used on the title page. It identifies the institution for the lab report.
2. `image2.png`: This shows the first `pthread01.c` program being edited in nano. The code creates a worker thread but does not wait for it.
3. `image3.png`: This shows compiling and running the first thread program. The output demonstrates that the main thread can exit before the worker thread prints.
4. `image4.png`: This shows the version with `sleep`. The worker thread prints before the main program exits because the process stays alive.
5. `image5.png`: This shows the version using `pthread_join`. The main thread exits only after the worker thread finishes.
6. `image6.png`: This shows the PID/TID inspection for one worker thread. The `ps -T` output lists the main thread and the worker thread under the same process ID.
7. `image7.png`: This shows the PID/TID inspection for two worker threads. The `ps -T` output lists three execution entries: main plus two workers.
8. `image8.png`: This shows two different thread tasks finishing. In this run, task 1 printed before task 2.
9. `image9.png`: This shows the distinct-task program while it is running, including the process ID and `ps -T` output. It confirms that both task threads exist at the same time.
10. `image10.png`: This shows both thread messages reporting the same PID. That confirms threads share one process.
11. `image11.png`: This shows the process version reporting different PIDs. That confirms `fork()` creates separate processes.
12. `image12.png`: This shows the global variable test with processes. One process reports `Global X: 3`, while the other reports `Global X: 2`, proving the global variable was copied, not shared.
13. `image13.png`: This shows the thread global-variable test. Both threads see `x` as `3`, proving they share the same global variable.
14. `image14.png`: This shows a race-condition result where the mail count is much lower than expected. The missing increments were caused by unsynchronized access.
15. `image15.png`: This shows the small-loop counter result of `200`. With only 100 increments per thread, the expected result was reached.
16. `image16.png`: This shows another race-condition run with a different incorrect count. The changing result proves the outcome depends on timing.
17. `image17.png`: This shows the mutex-protected four-thread result of `4000000`. The lock preserved correctness.
18. `image18.png`: This shows the four-thread program without the mutex producing an incorrect lower value. Removing the lock brought back the race condition.
19. `image19.png`: This shows semaphore threads printing without restriction or with minimal restriction. The messages appear as the scheduler allows them.
20. `image20.png`: This shows semaphore-controlled output where threads print in a controlled sequence.
21. `image21.png`: This shows the semaphore program printing all four thread messages. It demonstrates that all threads run, but access depends on the semaphore value.
22. `image22.png`: This shows a different semaphore output order. The order is not guaranteed because thread scheduling is nondeterministic.

## Results Summary

The lab showed that threads are useful because they allow multiple tasks to run inside the same process and share memory. The first thread examples showed why `pthread_join` is better than guessing with `sleep`. The process examples showed that `fork()` creates separate memory spaces, while threads share global variables.

The race-condition examples showed the danger of shared memory. When two or more threads updated `mails` without synchronization, the final count was incorrect because `mails++` is not atomic. Adding a mutex fixed the problem by protecting the critical section. Finally, the semaphore examples showed how a synchronization counter can either behave like a mutex when initialized to `1` or allow limited parallel access when initialized to a larger value.
