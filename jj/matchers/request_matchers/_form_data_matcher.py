from typing import Any, Dict

from packed import packable

from ...requests import Request
from ...resolvers import Resolver
from ..attribute_matchers import AttributeMatcher, MultiDictMatcher
from ._param_matcher import DictOrTupleListOrAttrMatcher
from ._request_matcher import RequestMatcher

__all__ = ("FormDataMatcher",)


@packable("jj.matchers.FormDataMatcher")
class FormDataMatcher(RequestMatcher):
    """
    Matches HTTP requests based on form data fields.

    This matcher checks if the incoming request's form data matches
    a specified set of fields, or a dynamic attribute-based matcher.
    The body is parsed by aiohttp according to the actual `Content-Type`
    header, so requests without a form body never produce a match.
    """

    def __init__(self, form_data: DictOrTupleListOrAttrMatcher, *, resolver: Resolver) -> None:
        """
        Initialize a FormDataMatcher with the specified form data and resolver.

        :param form_data: The form data fields to match against, either as a dictionary,
                          list of tuples, or a dynamic attribute matcher.
        :param resolver: The resolver responsible for registering this matcher.
        """
        super().__init__(resolver=resolver)
        if isinstance(form_data, AttributeMatcher):
            self._matcher = form_data
        else:
            self._matcher = MultiDictMatcher(form_data)

    @property
    def sub_matcher(self) -> AttributeMatcher:
        """
        Return the underlying attribute matcher used for form data matching.

        :return: The matcher that evaluates the request's form data.
        """
        return self._matcher

    async def match(self, request: Request) -> bool:
        """
        Determine if the request's form data matches the expected fields.

        :param request: The HTTP request containing the form data to match.
        :return: `True` if the request's form data matches, otherwise `False`.
        """
        try:
            await request.post()
        except Exception:
            return False
        return await self._matcher.match(request.post_data)

    def __repr__(self) -> str:
        """
        Return a string representation of the FormDataMatcher instance.

        :return: A string describing the class, matcher, and resolver.
        """
        return f"{self.__class__.__qualname__}({self._matcher!r}, resolver={self._resolver!r})"

    def __packed__(self) -> Dict[str, Any]:
        """
        Pack the FormDataMatcher instance for serialization.

        :return: A dictionary containing the serialized form of the matcher.
        """
        return {"form_data": self._matcher}

    @classmethod
    def __unpacked__(cls, *,
                     form_data: DictOrTupleListOrAttrMatcher,
                     resolver: Resolver,
                     **kwargs: Any) -> "FormDataMatcher":
        """
        Unpack a FormDataMatcher instance from its serialized form.

        :param form_data: The form data fields to use for this instance.
        :param resolver: The resolver to bind this matcher to.
        :param kwargs: Additional keyword arguments (ignored).
        :return: A new instance of FormDataMatcher.
        """
        return cls(form_data, resolver=resolver)
