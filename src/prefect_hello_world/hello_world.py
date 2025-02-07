"""
Simple Prefect Flow intended to be used as a playground for building event-driven
Deployments and testing out Prefect features.

Demonstrates:
* triggering custom events and passing parameters between Deployments.
* How failed flow-runs are handled by Prefect. How they can be retried both due to infra related issues and in program issues.
"""

import random
import time

from prefect import flow, get_run_logger, task
from prefect.events import emit_event

FAIL_PROBABILITY = 40

@task
def say_it(msg: str) -> None:
    logger = get_run_logger()
    logger.info(f"Hello world! {msg!r}")


@flow
def subflow(msg: str) -> None:
    say_it(msg)


@task(persist_result=True)
def task1() -> None:
    logger = get_run_logger()
    logger.info("Task 1")
    if random.randint(0, 100) < FAIL_PROBABILITY:
        raise Exception("!!!Task1 Unexpected exception!!!")


@task(retries=2, retry_delay_seconds=10, persist_result=True)
def task2() -> None:
    logger = get_run_logger()
    logger.info("Task 2")
    if random.randint(0, 100) < FAIL_PROBABILITY:
        raise Exception("!!!Task2 Unexpected exception!!!")


@task(retries=3, retry_delay_seconds=5, persist_result=True)
def task3() -> None:
    logger = get_run_logger()
    logger.info("Task 3")
    if random.randint(0, 100) < FAIL_PROBABILITY:
        raise Exception("!!!Task3 Unexpected exception!!!")


@flow(retries=6, retry_delay_seconds=5)
def hello_world(
    resource_id: str = "first", trigger_occurred: str = "2025-02-07T08:12:00Z", trigger_resource_json: str = "test", complete_event: str = "test", payload_dict_str: str = "test"
) -> str:
    subflow("hello world")
    random.seed(time.time())
    task1()
    task2()
    task3()

    if random.randint(0, 100) < FAIL_PROBABILITY:
        raise Exception("!!!Unexpected exception!!!")

    logger = get_run_logger()
    logger.info(f"complete_event: {complete_event!r}")
    logger.info(f"trigger_occurred: {trigger_occurred!r}")
    logger.info(f"trigger_resource: {trigger_resource_json!r}")
    # logger.info(f"payload_dict_str: {repr(ast.literal_eval(payload_dict_str))}") # FIXME: Until Compound trigger event is passed correctly to Flow
    emit_event(
        event="acme.hello-world.test-event",
        resource={"prefect.resource.id": f"acme.hello-world.{resource_id}"},
        payload={"data1": 101, "data2": "value2", "data3": [1, 2, 3, 4]})

    return "hello world"


if __name__ == "__main__":
    message = hello_world("first", "20241212", "bar", r'{"foo": "bar"}', "{}")
